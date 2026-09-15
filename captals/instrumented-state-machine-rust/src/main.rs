use captals_instrumented_state_machine::{
    BatchConfig, InstrumentedStateMachine, SamplingConfig,
};
use std::time::Duration;

#[derive(Debug, Clone)]
enum OrderState {
    Created,
    Processing,
    Completed,
    Failed,
}

#[tokio::main(flavor = "multi_thread")]
async fn main() {
    let (machine, batch_worker) = InstrumentedStateMachine::with_unbounded_batching(
        OrderState::Created,
        SamplingConfig {
            sample_rate: 1_000,
            min_duration_ms: 2,
        },
        BatchConfig {
            max_batch_size: 1_024,
            flush_interval: Duration::from_millis(250),
        },
    );

    for i in 0..10_000_u64 {
        let next_state = match i % 4 {
            0 => OrderState::Processing,
            1 => OrderState::Completed,
            2 => OrderState::Created,
            _ => OrderState::Failed,
        };

        let result = machine.transition(next_state, || {
            if i % 7 == 0 {
                return Err("simulated business failure".to_owned());
            }
            Ok(())
        });

        if result.is_err() {
            // The failure was already queued for sampled observability.
        }
    }

    println!("metrics={:?}", machine.metrics_snapshot());
    println!("state={:?}", machine.state_snapshot());

    drop(machine);
    let _ = batch_worker.await;
}
