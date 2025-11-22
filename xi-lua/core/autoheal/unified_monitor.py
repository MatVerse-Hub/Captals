#!/usr/bin/env python3
"""
Unified Monitor - Integration of AutoHeal + Stabilizer
=======================================================

This module integrates:
- LUA-AutoHeal (security & key rotation)
- Stabilizer-Recal (antifragility)
- Omega-Gate (quality control)

Provides a single interface for system-wide monitoring and control.

Part of Ξ-LUA v2.0 SuperProject
"""

import time
import threading
from datetime import datetime
from typing import Dict, Optional
import logging

from .lua_autoheal import get_autoheal, LuaAutoHeal
from ..stabilizer.stabilizer_recal import get_stabilizer, StabilizerRecal
from ..omniverse.omega_gate import OmegaGate

logger = logging.getLogger(__name__)


class UnifiedMonitor:
    """
    Unified monitoring and control system

    Monitors:
    - Security events (AutoHeal)
    - Risk levels (Stabilizer)
    - Quality metrics (Omega-Gate)

    Actions:
    - Auto-trigger kill-switch on critical events
    - Recalibrate Ψ-target based on CVaR
    - Log all events to Merkle chain
    """

    def __init__(self, monitor_interval: int = 5):
        """
        Initialize unified monitor

        Args:
            monitor_interval: How often to check system health (seconds)
        """
        self.monitor_interval = monitor_interval
        self.autoheal = get_autoheal()
        self.stabilizer = get_stabilizer()

        try:
            self.omega_gate = OmegaGate()
        except Exception as e:
            logger.warning(f"Omega-Gate not available: {e}")
            self.omega_gate = None

        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Statistics
        self.total_events = 0
        self.security_events = 0
        self.recalibrations = 0
        self.start_time = datetime.utcnow()

    def start(self):
        """Start unified monitoring"""
        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("🟢 Unified Monitor started")
        self.autoheal.logger.append("UnifiedMonitor started", {
            'monitor_interval': self.monitor_interval,
            'components': ['AutoHeal', 'Stabilizer', 'OmegaGate' if self.omega_gate else 'OmegaGate (disabled)']
        })

    def stop(self):
        """Stop unified monitoring"""
        if not self.running:
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        logger.info("🔴 Unified Monitor stopped")
        self.autoheal.logger.append("UnifiedMonitor stopped", {
            'total_events': self.total_events,
            'security_events': self.security_events,
            'recalibrations': self.recalibrations,
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
        })

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_system_health()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                self.autoheal.report_suspicious("monitor_error", {
                    'error': str(e)
                })

            time.sleep(self.monitor_interval)

    def _check_system_health(self):
        """Check health of all subsystems"""
        # Check AutoHeal status
        ah_status = self.autoheal.get_status()

        if ah_status['status'] != 'ACTIVE':
            logger.critical("🔴 AutoHeal KILL-SWITCH ACTIVATED!")
            # System should already be shutting down
            return

        # Check key age (warn if getting close to rotation)
        key_age = ah_status['current_key_age']
        if key_age > 270:  # 270s = 4.5 minutes (warning before 5min rotation)
            logger.debug(f"Key rotation imminent ({key_age}s / 300s)")

        # Check Merkle chain integrity
        if not ah_status['chain_integrity']:
            logger.critical("🔴 MERKLE CHAIN INTEGRITY COMPROMISED!")
            self.autoheal.report_suspicious("chain_integrity_failure", {
                'chain_length': ah_status['chain_length']
            })
            self.security_events += 1

        # Check Stabilizer CVaR
        stabilizer_state = self.stabilizer.state

        if stabilizer_state.cvar > 0.15:
            logger.warning(f"⚠️  High CVaR: {stabilizer_state.cvar:.4f}")

            # Report to AutoHeal
            self.autoheal.report_suspicious("high_cvar", {
                'cvar': stabilizer_state.cvar,
                'psi_target': stabilizer_state.psi_target,
                'attack_mode': stabilizer_state.attack_mode
            })
            self.security_events += 1

        # Track recalibrations
        if stabilizer_state.recalibration_count > self.recalibrations:
            self.recalibrations = stabilizer_state.recalibration_count
            logger.info(f"📈 System recalibrated (total: {self.recalibrations})")

        # Check Omega-Gate (if available)
        if self.omega_gate:
            try:
                omega_value = getattr(self.omega_gate, 'current_omega', None)
                if omega_value and omega_value < 0.85:
                    logger.warning(f"⚠️  Low Omega: {omega_value:.4f}")
                    self.autoheal.report_suspicious("low_omega", {
                        'omega': omega_value
                    })
            except Exception as e:
                logger.debug(f"Omega-Gate check failed: {e}")

        self.total_events += 1

    def report_event(self, event_type: str, details: Dict):
        """
        Report custom event to unified monitor

        Args:
            event_type: Type of event
            details: Event details
        """
        # Log to Merkle chain
        self.autoheal.logger.append(f"Event: {event_type}", details)

        # Check if suspicious
        suspicious_types = [
            'failed_auth',
            'invalid_signature',
            'rate_limit_exceeded',
            'unauthorized_access',
            'tampering_detected'
        ]

        if event_type in suspicious_types:
            self.autoheal.report_suspicious(event_type, details)
            self.security_events += 1

        self.total_events += 1

    def simulate_attack(self, duration: int = 10, cvar: float = 0.25):
        """
        Simulate attack for testing

        Args:
            duration: Attack duration in seconds
            cvar: Simulated CVaR value
        """
        logger.warning(f"🔴 SIMULATING ATTACK (CVaR={cvar:.2f}, duration={duration}s)")

        start = time.time()
        iteration = 0

        while time.time() - start < duration:
            # Update CVaR (may trigger recalibration)
            self.stabilizer.update_cvar(cvar)

            # Report suspicious events
            self.autoheal.report_suspicious("simulated_attack", {
                'iteration': iteration,
                'cvar': cvar,
                'elapsed': time.time() - start
            })

            iteration += 1
            time.sleep(0.5)

        logger.info(f"✅ Attack simulation complete ({iteration} iterations)")

    def get_unified_status(self) -> Dict:
        """Get complete system status"""
        ah_status = self.autoheal.get_status()
        stab_state = self.stabilizer.state

        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            'monitor': {
                'running': self.running,
                'uptime_seconds': uptime,
                'total_events': self.total_events,
                'security_events': self.security_events,
                'recalibrations': self.recalibrations
            },
            'autoheal': {
                'status': ah_status['status'],
                'key_rotations': ah_status['rotation_count'],
                'key_age': ah_status['current_key_age'],
                'merkle_root': ah_status['merkle_root'][:16] + '...',
                'chain_length': ah_status['chain_length'],
                'chain_integrity': ah_status['chain_integrity']
            },
            'stabilizer': {
                'mode': 'ATTACK' if stab_state.attack_mode else 'NORMAL',
                'psi_target': stab_state.psi_target,
                'cvar': stab_state.cvar,
                'price_multiplier': stab_state.price_multiplier,
                'recalibration_count': stab_state.recalibration_count
            },
            'omega_gate': {
                'available': self.omega_gate is not None,
                'threshold': self.omega_gate.omega_threshold if self.omega_gate else None
            }
        }


# Singleton instance
_monitor_instance: Optional[UnifiedMonitor] = None


def get_unified_monitor() -> UnifiedMonitor:
    """Get global UnifiedMonitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = UnifiedMonitor()
    return _monitor_instance


if __name__ == '__main__':
    print("=== Unified Monitor Test ===\n")

    monitor = get_unified_monitor()

    # Start monitoring
    print("1. Starting unified monitor...")
    monitor.start()
    time.sleep(2)

    # Report some events
    print("\n2. Reporting test events...")
    monitor.report_event("test_event", {'test': True})
    monitor.report_event("normal_operation", {'value': 42})
    time.sleep(1)

    # Check status
    print("\n3. Current status:")
    status = monitor.get_unified_status()
    for category, values in status.items():
        print(f"\n  {category}:")
        for key, value in values.items():
            print(f"    {key}: {value}")

    # Simulate attack
    print("\n4. Simulating attack...")
    monitor.simulate_attack(duration=6, cvar=0.22)

    # Final status
    print("\n5. Final status after attack:")
    status = monitor.get_unified_status()
    print(f"  Mode: {status['stabilizer']['mode']}")
    print(f"  Ψ-target: {status['stabilizer']['psi_target']:.4f}")
    print(f"  CVaR: {status['stabilizer']['cvar']:.4f}")
    print(f"  Security events: {status['monitor']['security_events']}")
    print(f"  Recalibrations: {status['monitor']['recalibrations']}")

    # Stop
    print("\n6. Stopping monitor...")
    monitor.stop()

    print("\n✅ Unified Monitor test complete!")
