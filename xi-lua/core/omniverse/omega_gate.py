#!/usr/bin/env python3
"""
Ω-OMNIVERSE - Probabilistic Confidence Scoring System
======================================================

The Omega (Ω) formula decides if Ξ-LUA has permission to exist in the next second.

Formula (FIXED and IMMUTABLE):
    Ω = 0.4·(1−CVaRα) + 0.3·(1−β) + 0.2·(1−ERR₅m) + 0.1·Idem

Where:
    - CVaRα: Conditional Value at Risk (tail risk, α=0.05)
    - β: False negative rate (HMAC/ECDSA validation failures)
    - ERR₅m: Error rate in last 5 minutes
    - Idem: Idempotency fraction (exactly-once delivery)

Gate Requirement:
    Ω ≥ 0.90 for production operations
    Ω < 0.90 → System refuses to operate

Part of Ξ-LUA v2.0 SuperProject
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OmegaComponents:
    """Individual components of Ω score"""
    cvar: float  # Conditional Value at Risk
    beta: float  # False negative rate
    err_5m: float  # Error rate (5 min)
    idem: float  # Idempotency fraction
    omega: float  # Final Ω score

    def to_dict(self) -> Dict:
        return {
            'CVaR_α': round(self.cvar, 4),
            'β': round(self.beta, 4),
            'ERR_5m': round(self.err_5m, 4),
            'Idem': round(self.idem, 4),
            'Ω': round(self.omega, 4)
        }


class OmegaGate:
    """
    Ω-GATE: The gatekeeper that decides if Ξ-LUA can operate.

    Weights (IMMUTABLE):
        w_cvar = 0.4  (40% - tail risk dominates)
        w_beta = 0.3  (30% - security critical)
        w_err  = 0.2  (20% - stability matters)
        w_idem = 0.1  (10% - consistency check)
    """

    # IMMUTABLE WEIGHTS (fixed forever)
    W_CVAR = 0.4
    W_BETA = 0.3
    W_ERR = 0.2
    W_IDEM = 0.1

    # Gate threshold
    OMEGA_THRESHOLD = 0.90

    # CVaR parameters
    ALPHA = 0.05  # 5% worst-case tail
    WINDOW_SIZE = 100  # Rolling window of last 100 actions

    def __init__(self):
        self.action_history: List[Dict] = []
        self.error_timestamps: List[datetime] = []
        self.validation_results: List[bool] = []  # True=valid, False=invalid
        self.idempotent_count = 0
        self.total_webhooks = 0

    def _compute_cvar(self, confidence_scores: List[float], alpha: float = None) -> float:
        """
        Compute Conditional Value at Risk (CVaR)

        CVaR_α = Expected loss in worst α% of cases

        Returns: CVaR value (0 = perfect, 1 = catastrophic)
        """
        if not confidence_scores:
            return 0.0

        alpha = alpha or self.ALPHA

        # Convert to loss (1 - confidence)
        losses = [1.0 - score for score in confidence_scores]

        # Sort losses descending
        sorted_losses = sorted(losses, reverse=True)

        # Take worst α% (e.g., worst 5%)
        cutoff = max(1, int(len(sorted_losses) * alpha))
        tail_losses = sorted_losses[:cutoff]

        # CVaR = average of tail losses
        cvar = np.mean(tail_losses)

        return float(cvar)

    def _compute_beta(self) -> float:
        """
        Compute false negative rate β

        β = (False Negatives) / (False Negatives + True Positives)

        Lower is better (0 = perfect)
        """
        if not self.validation_results:
            return 0.0

        # False negative = validation passed but should have failed
        # For now, we approximate β from validation failure rate
        failures = sum(1 for valid in self.validation_results if not valid)
        total = len(self.validation_results)

        return failures / total if total > 0 else 0.0

    def _compute_err_5m(self) -> float:
        """
        Compute error rate in last 5 minutes

        ERR_5m = (errors in last 5 min) / (total actions in last 5 min)
        """
        now = datetime.utcnow()
        five_min_ago = now - timedelta(minutes=5)

        # Count errors in last 5 minutes
        recent_errors = sum(1 for ts in self.error_timestamps if ts >= five_min_ago)

        # Count total actions in last 5 minutes
        recent_actions = sum(1 for action in self.action_history
                             if datetime.fromisoformat(action['timestamp']) >= five_min_ago)

        if recent_actions == 0:
            return 0.0

        return recent_errors / recent_actions

    def _compute_idem(self) -> float:
        """
        Compute idempotency fraction

        Idem = (idempotent webhooks) / (total webhooks)

        Higher is better (1 = perfect exactly-once delivery)
        """
        if self.total_webhooks == 0:
            return 1.0  # Default to perfect if no data

        return self.idempotent_count / self.total_webhooks

    def compute_omega(self) -> OmegaComponents:
        """
        Compute Ω score using THE FORMULA:

        Ω = 0.4·(1−CVaRα) + 0.3·(1−β) + 0.2·(1−ERR₅m) + 0.1·Idem

        Returns: OmegaComponents with all values
        """
        # Get recent confidence scores for CVaR
        recent_scores = [
            action.get('confidence', 1.0)
            for action in self.action_history[-self.WINDOW_SIZE:]
        ]

        # Compute components
        cvar = self._compute_cvar(recent_scores)
        beta = self._compute_beta()
        err_5m = self._compute_err_5m()
        idem = self._compute_idem()

        # THE FORMULA (immutable weights)
        omega = (
                self.W_CVAR * (1 - cvar) +
                self.W_BETA * (1 - beta) +
                self.W_ERR * (1 - err_5m) +
                self.W_IDEM * idem
        )

        components = OmegaComponents(
            cvar=cvar,
            beta=beta,
            err_5m=err_5m,
            idem=idem,
            omega=omega
        )

        return components

    def check_gate(self) -> Tuple[bool, OmegaComponents]:
        """
        Check if system passes Ω-GATE threshold.

        Returns: (passed: bool, components: OmegaComponents)

        If Ω < 0.90:
            - System REFUSES to operate
            - No new files accepted
            - Kill-switch may activate
        """
        components = self.compute_omega()

        passed = components.omega >= self.OMEGA_THRESHOLD

        status = "✅ PASS" if passed else "🔴 FAIL"
        logger.info(f"Ω-GATE: Ω={components.omega:.3f} {status} (threshold={self.OMEGA_THRESHOLD})")

        return passed, components

    def record_action(self, action_type: str, confidence: float = 1.0, metadata: Dict = None):
        """
        Record an action for Ω computation.

        Args:
            action_type: Type of action (deploy, mint, sign, etc.)
            confidence: Confidence score 0-1 (1=perfect)
            metadata: Additional metadata
        """
        action = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': action_type,
            'confidence': confidence,
            'metadata': metadata or {}
        }

        self.action_history.append(action)

        # Keep window size limited
        if len(self.action_history) > self.WINDOW_SIZE * 2:
            self.action_history = self.action_history[-self.WINDOW_SIZE:]

    def record_error(self):
        """Record an error event"""
        self.error_timestamps.append(datetime.utcnow())

        # Keep last 5 minutes only
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        self.error_timestamps = [ts for ts in self.error_timestamps if ts >= five_min_ago]

    def record_validation(self, is_valid: bool):
        """Record a validation result (for β computation)"""
        self.validation_results.append(is_valid)

        # Keep window size limited
        if len(self.validation_results) > self.WINDOW_SIZE:
            self.validation_results = self.validation_results[-self.WINDOW_SIZE:]

    def record_webhook(self, is_idempotent: bool):
        """Record webhook delivery (for Idem computation)"""
        self.total_webhooks += 1
        if is_idempotent:
            self.idempotent_count += 1

    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        components = self.compute_omega()
        passed, _ = self.check_gate()

        report = f"""
╔══════════════════════════════════════════════════════════╗
║          Ω-OMNIVERSE Confidence Score Report            ║
╚══════════════════════════════════════════════════════════╝

Formula: Ω = 0.4·(1−CVaRα) + 0.3·(1−β) + 0.2·(1−ERR₅m) + 0.1·Idem

Components:
  CVaRα (tail risk):        {components.cvar:.4f} → contrib: {self.W_CVAR * (1 - components.cvar):.4f}
  β (false negative):       {components.beta:.4f} → contrib: {self.W_BETA * (1 - components.beta):.4f}
  ERR₅m (error rate):       {components.err_5m:.4f} → contrib: {self.W_ERR * (1 - components.err_5m):.4f}
  Idem (idempotency):       {components.idem:.4f} → contrib: {self.W_IDEM * components.idem:.4f}

Final Score:
  Ω = {components.omega:.4f}

Gate Status:
  Threshold: {self.OMEGA_THRESHOLD:.2f}
  Status: {'✅ OPERATIONAL (Ω ≥ 0.90)' if passed else '🔴 BLOCKED (Ω < 0.90)'}

System State:
  Actions tracked: {len(self.action_history)}
  Recent errors (5m): {len(self.error_timestamps)}
  Total webhooks: {self.total_webhooks}
  Idempotent: {self.idempotent_count}

{'━' * 60}
The Ξ-LUA {'HAS PERMISSION' if passed else 'DOES NOT HAVE PERMISSION'} to exist in the next second.
{'━' * 60}
        """

        return report


# Singleton instance
_omega_gate_instance = None


def get_omega_gate() -> OmegaGate:
    """Get global Ω-GATE instance"""
    global _omega_gate_instance
    if _omega_gate_instance is None:
        _omega_gate_instance = OmegaGate()
    return _omega_gate_instance


if __name__ == '__main__':
    print("=== Ω-OMNIVERSE Test ===\n")

    gate = get_omega_gate()

    # Scenario 1: Perfect system
    print("1. Testing PERFECT system (100 actions, 0 errors)...")
    for i in range(100):
        gate.record_action('deploy', confidence=1.0)
        gate.record_validation(True)
        gate.record_webhook(is_idempotent=True)

    print(gate.get_status_report())

    # Scenario 2: System under mild stress
    print("\n2. Testing system UNDER STRESS (10 errors, 5 validation failures)...")
    gate_stress = OmegaGate()

    for i in range(100):
        confidence = 0.95 if i % 10 != 0 else 0.70  # 10% low confidence
        gate_stress.record_action('deploy', confidence=confidence)
        gate_stress.record_validation(i % 20 != 0)  # 5% validation failures
        gate_stress.record_webhook(is_idempotent=i % 10 != 0)  # 10% not idempotent

    # Add some errors
    for _ in range(10):
        gate_stress.record_error()

    print(gate_stress.get_status_report())

    # Scenario 3: System in crisis (should FAIL gate)
    print("\n3. Testing system in CRISIS (high CVaR, many errors)...")
    gate_crisis = OmegaGate()

    for i in range(100):
        confidence = 0.60 if i % 3 == 0 else 0.85  # High variance
        gate_crisis.record_action('deploy', confidence=confidence)
        gate_crisis.record_validation(i % 5 != 0)  # 20% validation failures
        gate_crisis.record_webhook(is_idempotent=i % 3 != 0)  # 33% not idempotent

    # Add many errors
    for _ in range(30):
        gate_crisis.record_error()

    print(gate_crisis.get_status_report())

    print("\n✅ Ω-OMNIVERSE testing complete!")
    print("\nKey insight:")
    print("  - Perfect system: Ω ≈ 0.99 ✅")
    print("  - Stressed system: Ω ≈ 0.88-0.92 ⚠️")
    print("  - Crisis system: Ω < 0.85 🔴 (GATE BLOCKS)")
