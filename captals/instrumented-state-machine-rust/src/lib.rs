//! Generic, high-frequency state transitions with lock-free metrics and sampled tracing.
//!
//! The business closure runs outside the state lock. On success, the candidate state is
//! committed under a short `RwLock` write section. Concurrent successful transitions use
//! last-successful-writer-wins semantics; domains requiring strict serial transition order
//! should place this type behind a single actor or an external mutex.

use std::{
    fmt::Debug,
    sync::{
        atomic::{AtomicU64, Ordering},
        RwLock,
    },
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

use tokio::{
    sync::mpsc::{self, UnboundedReceiver, UnboundedSender},
    task::JoinHandle,
    time::{self, MissedTickBehavior},
};
use tracing::{event, Level};

/// Sampling policy for successful transitions. Failures are always emitted.
#[derive(Debug, Clone, Copy)]
pub struct SamplingConfig {
    /// Emit one representative successful transition every N transitions. Zero disables periodic sampling.
    pub sample_rate: u64,
    /// Emit successful transitions slower than this threshold; transitions slower than 10x use WARN.
    pub min_duration_ms: u128,
}

impl Default for SamplingConfig {
    fn default() -> Self {
        Self {
            sample_rate: 1_000,
            min_duration_ms: 5,
        }
    }
}

/// Batch worker configuration. This affects observability only, never state execution.
#[derive(Debug, Clone, Copy)]
pub struct BatchConfig {
    pub max_batch_size: usize,
    pub flush_interval: Duration,
}

impl Default for BatchConfig {
    fn default() -> Self {
        Self {
            max_batch_size: 1_024,
            flush_interval: Duration::from_millis(250),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TransitionReceipt {
    pub transition_id: u64,
    pub duration_ms: u128,
    pub instrumented: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MetricsSnapshot {
    pub transition_count: u64,
    pub success_count: u64,
    pub failure_count: u64,
    pub instrumented_count: u64,
    pub dropped_log_events: u64,
    pub total_duration_ms: u64,
    pub max_duration_ms: u64,
    pub last_transition_unix_ms: u64,
}

#[derive(Debug)]
struct TransitionEvent<S> {
    transition_id: u64,
    state: S,
    duration_ms: u128,
    success: bool,
}

/// Generic state machine with short lock hold-times and sampled observability.
#[derive(Debug)]
pub struct InstrumentedStateMachine<S> {
    state: RwLock<S>,
    sampling: SamplingConfig,
    transition_count: AtomicU64,
    success_count: AtomicU64,
    failure_count: AtomicU64,
    instrumented_count: AtomicU64,
    dropped_log_events: AtomicU64,
    total_duration_ms: AtomicU64,
    max_duration_ms: AtomicU64,
    last_transition_unix_ms: AtomicU64,
    log_sender: Option<UnboundedSender<TransitionEvent<S>>>,
}

impl<S> InstrumentedStateMachine<S>
where
    S: Clone + Debug + Send + Sync + 'static,
{
    pub fn new(initial_state: S, sampling: SamplingConfig) -> Self {
        Self::with_sender(initial_state, sampling, None)
    }

    /// Creates a machine and an off-thread worker that aggregates sampled events.
    pub fn with_unbounded_batching(
        initial_state: S,
        sampling: SamplingConfig,
        batch: BatchConfig,
    ) -> (Self, JoinHandle<()>) {
        let (sender, receiver) = mpsc::unbounded_channel();
        let machine = Self::with_sender(initial_state, sampling, Some(sender));
        let worker = spawn_batch_worker(receiver, batch);
        (machine, worker)
    }

    fn with_sender(
        initial_state: S,
        sampling: SamplingConfig,
        log_sender: Option<UnboundedSender<TransitionEvent<S>>>,
    ) -> Self {
        Self {
            state: RwLock::new(initial_state),
            sampling,
            transition_count: AtomicU64::new(0),
            success_count: AtomicU64::new(0),
            failure_count: AtomicU64::new(0),
            instrumented_count: AtomicU64::new(0),
            dropped_log_events: AtomicU64::new(0),
            total_duration_ms: AtomicU64::new(0),
            max_duration_ms: AtomicU64::new(0),
            last_transition_unix_ms: AtomicU64::new(0),
            log_sender,
        }
    }

    /// Returns a cloned snapshot. Read locks are brief and never held during business logic.
    pub fn state_snapshot(&self) -> S {
        self.state
            .read()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .clone()
    }

    pub fn metrics_snapshot(&self) -> MetricsSnapshot {
        MetricsSnapshot {
            transition_count: self.transition_count.load(Ordering::Relaxed),
            success_count: self.success_count.load(Ordering::Relaxed),
            failure_count: self.failure_count.load(Ordering::Relaxed),
            instrumented_count: self.instrumented_count.load(Ordering::Relaxed),
            dropped_log_events: self.dropped_log_events.load(Ordering::Relaxed),
            total_duration_ms: self.total_duration_ms.load(Ordering::Relaxed),
            max_duration_ms: self.max_duration_ms.load(Ordering::Relaxed),
            last_transition_unix_ms: self.last_transition_unix_ms.load(Ordering::Relaxed),
        }
    }

    /// Base sampling decision for successful transitions.
    /// Errors are emitted by `transition` regardless of this result.
    pub fn should_instrument(&self, count: u64, duration_ms: u128) -> bool {
        let extreme_slow_ms = self.sampling.min_duration_ms.saturating_mul(10);
        if duration_ms > extreme_slow_ms {
            return true;
        }

        self.sampling.sample_rate != 0 && count % self.sampling.sample_rate == 0
    }

    /// Executes business logic without a state lock and commits `new_state` only on success.
    pub fn transition<F>(&self, new_state: S, logic: F) -> Result<TransitionReceipt, String>
    where
        F: FnOnce() -> Result<(), String>,
    {
        let transition_id = self.transition_count.fetch_add(1, Ordering::Relaxed) + 1;
        let started_at = Instant::now();
        let result = logic();
        let duration_ms = started_at.elapsed().as_millis();
        self.observe_duration(duration_ms);
        self.last_transition_unix_ms
            .store(unix_time_ms(), Ordering::Relaxed);

        let success = result.is_ok();
        let slow = duration_ms > self.sampling.min_duration_ms;
        let instrumented = !success || slow || self.should_instrument(transition_id, duration_ms);
        let event_state = instrumented.then(|| new_state.clone());

        match result {
            Ok(()) => {
                *self
                    .state
                    .write()
                    .unwrap_or_else(|poisoned| poisoned.into_inner()) = new_state;
                self.success_count.fetch_add(1, Ordering::Relaxed);

                if let Some(state) = event_state {
                    self.emit(TransitionEvent {
                        transition_id,
                        state,
                        duration_ms,
                        success: true,
                    });
                }

                Ok(TransitionReceipt {
                    transition_id,
                    duration_ms,
                    instrumented,
                })
            }
            Err(error) => {
                self.failure_count.fetch_add(1, Ordering::Relaxed);

                if let Some(state) = event_state {
                    self.emit(TransitionEvent {
                        transition_id,
                        state,
                        duration_ms,
                        success: false,
                    });
                }

                Err(error)
            }
        }
    }

    fn observe_duration(&self, duration_ms: u128) {
        let duration_ms = saturating_u64(duration_ms);
        self.total_duration_ms
            .fetch_add(duration_ms, Ordering::Relaxed);

        let mut previous = self.max_duration_ms.load(Ordering::Relaxed);
        while duration_ms > previous {
            match self.max_duration_ms.compare_exchange_weak(
                previous,
                duration_ms,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(observed) => previous = observed,
            }
        }
    }

    fn emit(&self, transition_event: TransitionEvent<S>) {
        self.instrumented_count.fetch_add(1, Ordering::Relaxed);

        if let Some(sender) = &self.log_sender {
            if sender.send(transition_event).is_err() {
                self.dropped_log_events.fetch_add(1, Ordering::Relaxed);
            }
            return;
        }

        emit_direct(&transition_event, self.sampling);
    }
}

/// Groups events that already passed the sampling decision. The transition path never awaits it.
fn spawn_batch_worker<S>(
    mut receiver: UnboundedReceiver<TransitionEvent<S>>,
    batch_config: BatchConfig,
) -> JoinHandle<()>
where
    S: Debug + Send + 'static,
{
    let batch_size = batch_config.max_batch_size.max(1);
    let flush_interval = if batch_config.flush_interval.is_zero() {
        Duration::from_millis(250)
    } else {
        batch_config.flush_interval
    };

    tokio::spawn(async move {
        let mut ticker = time::interval(flush_interval);
        ticker.set_missed_tick_behavior(MissedTickBehavior::Skip);
        let mut batch = Vec::with_capacity(batch_size);

        loop {
            tokio::select! {
                maybe_event = receiver.recv() => match maybe_event {
                    Some(event) => {
                        batch.push(event);
                        if batch.len() >= batch_size {
                            emit_batch(&batch);
                            batch.clear();
                        }
                    }
                    None => {
                        if !batch.is_empty() {
                            emit_batch(&batch);
                        }
                        break;
                    }
                },
                _ = ticker.tick() => {
                    if !batch.is_empty() {
                        emit_batch(&batch);
                        batch.clear();
                    }
                }
            }
        }
    })
}

fn emit_direct<S>(transition_event: &TransitionEvent<S>, sampling: SamplingConfig)
where
    S: Debug,
{
    let status = if transition_event.success { "OK" } else { "ERR" };
    let extreme = transition_event.duration_ms > sampling.min_duration_ms.saturating_mul(10);

    if !transition_event.success || extreme {
        event!(
            target: "instrumented_state_machine.transition",
            Level::WARN,
            transition_id = transition_event.transition_id,
            state = ?transition_event.state,
            duration_ms = saturating_u64(transition_event.duration_ms),
            status = status,
            "sampled state transition"
        );
    } else {
        event!(
            target: "instrumented_state_machine.transition",
            Level::INFO,
            transition_id = transition_event.transition_id,
            state = ?transition_event.state,
            duration_ms = saturating_u64(transition_event.duration_ms),
            status = status,
            "sampled state transition"
        );
    }
}

fn emit_batch<S>(batch: &[TransitionEvent<S>])
where
    S: Debug,
{
    let error_count = batch.iter().filter(|event| !event.success).count() as u64;
    let success_count = batch.len() as u64 - error_count;
    let max_duration_ms = batch
        .iter()
        .map(|event| event.duration_ms)
        .max()
        .unwrap_or_default();
    let last = batch.last().expect("batch is checked before emission");

    event!(
        target: "instrumented_state_machine.batch",
        Level::INFO,
        batch_size = batch.len() as u64,
        success_count = success_count,
        error_count = error_count,
        max_duration_ms = saturating_u64(max_duration_ms),
        last_state = ?last.state,
        "instrumented state transition batch"
    );
}

fn saturating_u64(value: u128) -> u64 {
    value.min(u64::MAX as u128) as u64
}

fn unix_time_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
        .min(u64::MAX as u128) as u64
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Clone, Debug, PartialEq, Eq)]
    enum TestState {
        Created,
        Processing,
        Failed,
    }

    #[test]
    fn failed_logic_does_not_commit_candidate_state() {
        let machine = InstrumentedStateMachine::new(TestState::Created, SamplingConfig::default());
        let result = machine.transition(TestState::Failed, || Err("expected failure".to_owned()));

        assert!(result.is_err());
        assert_eq!(machine.state_snapshot(), TestState::Created);
        assert_eq!(machine.metrics_snapshot().failure_count, 1);
    }

    #[test]
    fn periodic_sampling_marks_representative_successes() {
        let machine = InstrumentedStateMachine::new(
            TestState::Created,
            SamplingConfig {
                sample_rate: 2,
                min_duration_ms: u128::MAX,
            },
        );

        let first = machine.transition(TestState::Processing, || Ok(())).unwrap();
        let second = machine.transition(TestState::Created, || Ok(())).unwrap();

        assert!(!first.instrumented);
        assert!(second.instrumented);
        assert_eq!(machine.metrics_snapshot().success_count, 2);
    }

    #[tokio::test]
    async fn batch_worker_drains_after_machine_drop() {
        let (machine, worker) = InstrumentedStateMachine::with_unbounded_batching(
            TestState::Created,
            SamplingConfig {
                sample_rate: 1,
                min_duration_ms: u128::MAX,
            },
            BatchConfig {
                max_batch_size: 2,
                flush_interval: Duration::from_secs(1),
            },
        );

        machine.transition(TestState::Processing, || Ok(())).unwrap();
        drop(machine);
        worker.await.unwrap();
    }
}
