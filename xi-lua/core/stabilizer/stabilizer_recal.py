#!/usr/bin/env python3
"""
Stabilizer_Recal - Antifragile Recalibration System
====================================================

Core Principle: "What doesn't kill you makes you stronger"

When the system detects high risk (CVaR > threshold):
1. Automatically increases Ψ-target (quality threshold)
2. Requires more gas for next operations
3. System becomes MORE SELECTIVE under attack
4. Attack = Revenue increase (higher prices)

This is TRUE ANTIFRAGILITY:
- Normal operation: Low cost, high throughput
- Under attack: High cost, low throughput, but HIGHER QUALITY
- Post-attack: Returns to normal with learned resilience

Bifurcation Point:
    k = 0.5 (critical point of chaotic bifurcation)
    If CVaR > 0.15 for more than 5 seconds → recalibrate

Part of Ξ-LUA v2.0 SuperProject
"""

import time
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [Stabilizer] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Current state of the system"""
    psi_target: float  # Quality threshold Ψ
    cvar: float  # Current CVaR
    price_multiplier: float  # Price multiplier (1.0 = normal)
    last_recalibration: datetime
    recalibration_count: int
    attack_mode: bool


class StabilizerRecal:
    """
    Antifragile Stabilizer with Automatic Recalibration

    Constants (IMMUTABLE):
        k = 0.5         (bifurcation constant)
        CVaR_threshold = 0.15  (danger zone)
        window = 5 seconds     (confirmation period)
        Ψ_min = 0.85    (minimum quality)
        Ψ_max = 0.98    (maximum quality)
        Ψ_default = 0.90 (normal operation)
    """

    # IMMUTABLE CONSTANTS
    K_BIFURCATION = 0.5  # Critical point
    CVAR_THRESHOLD = 0.15  # CVaR danger threshold
    CONFIRMATION_WINDOW = 5  # seconds
    PSI_MIN = 0.85
    PSI_MAX = 0.98
    PSI_DEFAULT = 0.90
    PSI_INCREMENT = 0.02  # Increase Ψ by 2% on each recalibration

    # Price adjustment factors
    PRICE_INCREMENT = 0.20  # Increase price by 20% per recalibration
    MAX_PRICE_MULTIPLIER = 3.0  # Max 3x price increase

    def __init__(self, initial_psi: float = None):
        self.state = SystemState(
            psi_target=initial_psi or self.PSI_DEFAULT,
            cvar=0.0,
            price_multiplier=1.0,
            last_recalibration=datetime.utcnow(),
            recalibration_count=0,
            attack_mode=False
        )

        # CVaR history for confirmation window
        self.cvar_history: List[Dict] = []

        # State history for analysis
        self.state_history: List[Dict] = []

        logger.info(f"Stabilizer initialized: Ψ={self.state.psi_target:.2f}")

    def update_cvar(self, cvar: float):
        """
        Update current CVaR and check if recalibration needed

        Args:
            cvar: Current Conditional Value at Risk (0-1)

        Returns:
            bool: True if recalibration occurred
        """
        now = datetime.utcnow()

        # Record CVaR
        self.cvar_history.append({
            'timestamp': now,
            'cvar': cvar
        })

        # Keep only recent history (last 10 seconds)
        cutoff = now - timedelta(seconds=10)
        self.cvar_history = [
            entry for entry in self.cvar_history
            if entry['timestamp'] >= cutoff
        ]

        # Update current CVaR
        self.state.cvar = cvar

        # Check if recalibration needed
        if self._should_recalibrate():
            self._recalibrate()
            return True

        return False

    def _should_recalibrate(self) -> bool:
        """
        Check if recalibration is needed

        Condition: CVaR > 0.15 for at least 5 consecutive seconds
        """
        if not self.cvar_history:
            return False

        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.CONFIRMATION_WINDOW)

        # Get all CVaR values in confirmation window
        recent_cvars = [
            entry['cvar']
            for entry in self.cvar_history
            if entry['timestamp'] >= window_start
        ]

        if not recent_cvars:
            return False

        # Check if ALL recent CVaRs exceed threshold
        all_above_threshold = all(cvar > self.CVAR_THRESHOLD for cvar in recent_cvars)

        # Need at least 3 samples in window
        sufficient_samples = len(recent_cvars) >= 3

        return all_above_threshold and sufficient_samples

    def _recalibrate(self):
        """
        Perform antifragile recalibration:
        1. Increase Ψ-target (higher quality requirement)
        2. Increase price multiplier
        3. Enter attack mode
        """
        old_psi = self.state.psi_target
        old_price = self.state.price_multiplier

        # Increase Ψ-target
        new_psi = min(self.PSI_MAX, old_psi + self.PSI_INCREMENT)

        # Increase price
        new_price = min(self.MAX_PRICE_MULTIPLIER, old_price * (1 + self.PRICE_INCREMENT))

        # Update state
        self.state.psi_target = new_psi
        self.state.price_multiplier = new_price
        self.state.last_recalibration = datetime.utcnow()
        self.state.recalibration_count += 1
        self.state.attack_mode = True

        # Log recalibration
        logger.warning(f"🔴 RECALIBRATION #{self.state.recalibration_count}")
        logger.warning(f"   CVaR: {self.state.cvar:.4f} > {self.CVAR_THRESHOLD}")
        logger.warning(f"   Ψ: {old_psi:.2f} → {new_psi:.2f} (+{self.PSI_INCREMENT:.2f})")
        logger.warning(f"   Price: {old_price:.2f}x → {new_price:.2f}x")
        logger.warning(f"   Status: ATTACK MODE ACTIVATED")

        # Record in history
        self.state_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'recalibration',
            'old_psi': old_psi,
            'new_psi': new_psi,
            'old_price': old_price,
            'new_price': new_price,
            'cvar': self.state.cvar,
            'count': self.state.recalibration_count
        })

    def try_relax(self) -> bool:
        """
        Try to relax constraints if system has been stable

        Condition: CVaR < 0.10 for at least 30 seconds

        Returns:
            bool: True if relaxation occurred
        """
        if not self.state.attack_mode:
            return False

        now = datetime.utcnow()
        stability_window = now - timedelta(seconds=30)

        # Get recent CVaRs
        recent_cvars = [
            entry['cvar']
            for entry in self.cvar_history
            if entry['timestamp'] >= stability_window
        ]

        if not recent_cvars:
            return False

        # Check if ALL recent CVaRs are below relaxation threshold
        all_below = all(cvar < 0.10 for cvar in recent_cvars)
        sufficient_samples = len(recent_cvars) >= 10

        if all_below and sufficient_samples:
            self._relax()
            return True

        return False

    def _relax(self):
        """
        Relax constraints after stability confirmed
        """
        old_psi = self.state.psi_target
        old_price = self.state.price_multiplier

        # Decrease Ψ-target (but not below default)
        new_psi = max(self.PSI_DEFAULT, old_psi - self.PSI_INCREMENT)

        # Decrease price (but not below 1.0)
        new_price = max(1.0, old_price / (1 + self.PRICE_INCREMENT))

        # Update state
        self.state.psi_target = new_psi
        self.state.price_multiplier = new_price

        # Exit attack mode if back to normal
        if new_psi <= self.PSI_DEFAULT and new_price <= 1.0:
            self.state.attack_mode = False
            logger.info("✅ ATTACK MODE DEACTIVATED - System normalized")

        logger.info(f"🟢 RELAXATION")
        logger.info(f"   CVaR: {self.state.cvar:.4f} (stable)")
        logger.info(f"   Ψ: {old_psi:.2f} → {new_psi:.2f} (-{self.PSI_INCREMENT:.2f})")
        logger.info(f"   Price: {old_price:.2f}x → {new_price:.2f}x")

        # Record in history
        self.state_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'relaxation',
            'old_psi': old_psi,
            'new_psi': new_psi,
            'old_price': old_price,
            'new_price': new_price,
            'cvar': self.state.cvar
        })

    def get_adjusted_price(self, base_price: float) -> float:
        """
        Get price adjusted for current system state

        Args:
            base_price: Base price in normal conditions

        Returns:
            Adjusted price based on current multiplier
        """
        return base_price * self.state.price_multiplier

    def should_accept_action(self, action_quality: float) -> bool:
        """
        Check if action meets current Ψ-target quality requirement

        Args:
            action_quality: Quality score of proposed action (0-1)

        Returns:
            bool: True if quality meets threshold
        """
        return action_quality >= self.state.psi_target

    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        state = self.state

        mode_emoji = "🔴" if state.attack_mode else "🟢"
        mode_text = "ATTACK MODE" if state.attack_mode else "NORMAL"

        time_since_recal = datetime.utcnow() - state.last_recalibration
        time_str = f"{int(time_since_recal.total_seconds())}s ago"

        report = f"""
╔══════════════════════════════════════════════════════════╗
║         Stabilizer-Recal Antifragility Status           ║
╚══════════════════════════════════════════════════════════╝

System Mode: {mode_emoji} {mode_text}

Current State:
  Ψ-target (quality):    {state.psi_target:.4f}
  CVaR (risk):           {state.cvar:.4f}
  Price multiplier:      {state.price_multiplier:.2f}x

Thresholds:
  CVaR threshold:        {self.CVAR_THRESHOLD:.2f}
  {'⚠️ ABOVE THRESHOLD' if state.cvar > self.CVAR_THRESHOLD else '✅ Below threshold'}

Recalibration History:
  Total recalibrations:  {state.recalibration_count}
  Last recalibration:    {time_str}

Attack Response:
  Normal price:          1.00x
  Current price:         {state.price_multiplier:.2f}x
  {'↑ System is MORE SELECTIVE under attack' if state.attack_mode else '✓ Operating normally'}

{'━' * 60}
Antifragility: {'ACTIVE - System gains strength from attack' if state.attack_mode else 'Ready to activate if needed'}
{'━' * 60}
        """

        return report


# Singleton instance
_stabilizer_instance: Optional[StabilizerRecal] = None


def get_stabilizer() -> StabilizerRecal:
    """Get global Stabilizer instance"""
    global _stabilizer_instance
    if _stabilizer_instance is None:
        _stabilizer_instance = StabilizerRecal()
    return _stabilizer_instance


if __name__ == '__main__':
    print("=== Stabilizer-Recal Antifragility Test ===\n")

    stabilizer = get_stabilizer()

    # Test 1: Normal operation
    print("1. Normal operation (CVaR = 0.05)...")
    for _ in range(10):
        stabilizer.update_cvar(0.05)
        time.sleep(0.1)

    print(stabilizer.get_status_report())

    # Test 2: Trigger recalibration
    print("\n2. Simulating attack (CVaR = 0.20 for 6 seconds)...")
    for i in range(60):  # 6 seconds at 10 updates/sec
        recalibrated = stabilizer.update_cvar(0.20)
        if recalibrated:
            print(f"   ⚠️ Recalibration triggered at iteration {i}")
        time.sleep(0.1)

    print(stabilizer.get_status_report())

    # Test 3: Price adjustment
    print("\n3. Price adjustment example:")
    base_prices = {
        'quick_audit': 23.92,
        'full_audit': 159.20
    }

    for name, base_price in base_prices.items():
        adjusted = stabilizer.get_adjusted_price(base_price)
        print(f"   {name}: R$ {base_price:.2f} → R$ {adjusted:.2f}")

    # Test 4: Try relaxation
    print("\n4. Simulating stability (CVaR = 0.08 for 35 seconds)...")
    for i in range(350):  # 35 seconds
        relaxed = stabilizer.try_relax()
        stabilizer.update_cvar(0.08)
        if relaxed:
            print(f"   ✅ Relaxation occurred at iteration {i}")
        time.sleep(0.1)

    print(stabilizer.get_status_report())

    print("\n✅ Stabilizer-Recal antifragility test complete!")
    print("\nKey insight:")
    print("  - Under attack → Ψ↑, Price↑ (system becomes stronger)")
    print("  - Stable → Ψ↓, Price↓ (system relaxes)")
    print("  - TRUE ANTIFRAGILITY in action! 🚀")
