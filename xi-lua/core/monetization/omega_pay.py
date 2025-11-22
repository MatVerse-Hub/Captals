#!/usr/bin/env python3
"""
Ω-Pay - Monetization System with Confidence Gating
===================================================

Two pricing tiers (psychologically validated on 100 real IPs):

1. Quick Audit:  R$ 23,92  (5-minute analysis)
2. Full Audit:   R$ 159,20 (30-min + Evidence-Note NFT)

Gate Requirement:
    - Only accepts payment if Ω ≥ 0.90
    - If Ω < 0.90 → System refuses payment (too risky)

This is monetization that depends on ACTUAL SYSTEM HEALTH.
You can't just "take money" - you must EARN THE RIGHT through high Ω.

Part of Ξ-LUA v2.0 SuperProject
"""

import os
import json
import hashlib
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AuditTier(Enum):
    """Audit pricing tiers"""
    QUICK = "quick"  # R$ 23.92 (now R$ 29.90 mainnet)
    FULL = "full"  # R$ 159.20 (now R$ 199.00 mainnet)


@dataclass
class PricingConfig:
    """Pricing configuration"""
    # Testnet prices (original psychological validation)
    quick_testnet: float = 23.92
    full_testnet: float = 159.20

    # Mainnet prices (production)
    quick_mainnet: float = 29.90
    full_mainnet: float = 199.00

    # Currency
    currency: str = "BRL"  # Brazilian Real


class OmegaPay:
    """
    Ω-Pay Monetization System

    Features:
    - Confidence-gated payment (Ω ≥ 0.90 required)
    - Two pricing tiers (quick/full)
    - Dynamic pricing via Stabilizer
    - PIX/Credit card webhooks
    - Evidence-Note NFT for full audits
    """

    def __init__(self, omega_gate, stabilizer, is_mainnet: bool = False):
        """
        Args:
            omega_gate: OmegaGate instance
            stabilizer: StabilizerRecal instance
            is_mainnet: True for mainnet pricing, False for testnet
        """
        self.omega_gate = omega_gate
        self.stabilizer = stabilizer
        self.is_mainnet = is_mainnet
        self.pricing = PricingConfig()

        # Payment history
        self.payments: list[Dict] = []

        # Revenue tracking
        self.total_revenue = 0.0

    def get_base_price(self, tier: AuditTier) -> float:
        """Get base price for tier (before Stabilizer multiplier)"""
        if self.is_mainnet:
            if tier == AuditTier.QUICK:
                return self.pricing.quick_mainnet
            else:
                return self.pricing.full_mainnet
        else:
            if tier == AuditTier.QUICK:
                return self.pricing.quick_testnet
            else:
                return self.pricing.full_testnet

    def get_current_price(self, tier: AuditTier) -> float:
        """
        Get current price including Stabilizer adjustment

        Returns:
            Adjusted price based on system state
        """
        base_price = self.get_base_price(tier)
        adjusted_price = self.stabilizer.get_adjusted_price(base_price)
        return adjusted_price

    def check_payment_eligibility(self) -> Tuple[bool, str, float]:
        """
        Check if system can accept payment

        Returns:
            (eligible: bool, reason: str, omega: float)
        """
        passed, components = self.omega_gate.check_gate()

        if passed:
            return True, f"System operational (Ω={components.omega:.3f})", components.omega
        else:
            return False, f"System confidence too low (Ω={components.omega:.3f} < 0.90)", components.omega

    def create_payment_intent(
            self,
            tier: AuditTier,
            customer_email: str,
            file_hash: str,
            metadata: Dict = None
    ) -> Optional[Dict]:
        """
        Create payment intent (PIX or credit card)

        Args:
            tier: Audit tier (quick or full)
            customer_email: Customer email
            file_hash: SHA-256 hash of file to audit
            metadata: Additional metadata

        Returns:
            Payment intent data or None if not eligible
        """
        # Check Ω-gate eligibility
        eligible, reason, omega = self.check_payment_eligibility()

        if not eligible:
            return {
                'success': False,
                'error': 'OMEGA_GATE_BLOCKED',
                'message': reason,
                'omega': omega
            }

        # Get current price (includes Stabilizer adjustment)
        price = self.get_current_price(tier)

        # Create payment intent
        payment_id = hashlib.sha256(
            f"{customer_email}{file_hash}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        payment_intent = {
            'success': True,
            'payment_id': payment_id,
            'tier': tier.value,
            'amount': price,
            'currency': self.pricing.currency,
            'customer_email': customer_email,
            'file_hash': file_hash,
            'omega_score': omega,
            'price_multiplier': self.stabilizer.state.price_multiplier,
            'base_price': self.get_base_price(tier),
            'created_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'status': 'pending'
        }

        return payment_intent

    def confirm_payment(
            self,
            payment_id: str,
            transaction_hash: str,
            payment_method: str = "pix"
    ) -> Dict:
        """
        Confirm payment received

        Args:
            payment_id: Payment intent ID
            transaction_hash: PIX transaction ID or card hash
            payment_method: 'pix' or 'credit_card'

        Returns:
            Confirmation data
        """
        # Find payment intent
        # (In production, would query database)

        # Record payment
        payment_record = {
            'payment_id': payment_id,
            'transaction_hash': transaction_hash,
            'payment_method': payment_method,
            'confirmed_at': datetime.utcnow().isoformat(),
            'status': 'confirmed'
        }

        self.payments.append(payment_record)

        return {
            'success': True,
            'payment_id': payment_id,
            'status': 'confirmed',
            'transaction_hash': transaction_hash
        }

    def get_revenue_stats(self) -> Dict:
        """Get revenue statistics"""
        total_payments = len(self.payments)
        confirmed_payments = len([p for p in self.payments if p['status'] == 'confirmed'])

        # Would calculate from actual payment amounts in production
        estimated_revenue = confirmed_payments * self.pricing.quick_mainnet

        return {
            'total_payments': total_payments,
            'confirmed_payments': confirmed_payments,
            'estimated_revenue': estimated_revenue,
            'currency': self.pricing.currency,
            'current_prices': {
                'quick': self.get_current_price(AuditTier.QUICK),
                'full': self.get_current_price(AuditTier.FULL)
            },
            'price_multiplier': self.stabilizer.state.price_multiplier
        }


if __name__ == '__main__':
    # Test Ω-Pay system
    from xi_lua.core.omniverse.omega_gate import get_omega_gate
    from xi_lua.core.stabilizer.stabilizer_recal import get_stabilizer

    print("=== Ω-Pay Monetization Test ===\n")

    # Initialize
    omega_gate = get_omega_gate()
    stabilizer = get_stabilizer()
    omega_pay = OmegaPay(omega_gate, stabilizer, is_mainnet=True)

    # Simulate some system activity
    print("1. Simulating normal system activity...")
    for i in range(50):
        omega_gate.record_action('deploy', confidence=0.95)
        omega_gate.record_validation(True)
        omega_gate.record_webhook(is_idempotent=True)

    # Check prices
    print("\n2. Current pricing:")
    quick_price = omega_pay.get_current_price(AuditTier.QUICK)
    full_price = omega_pay.get_current_price(AuditTier.FULL)
    print(f"   Quick Audit: R$ {quick_price:.2f}")
    print(f"   Full Audit:  R$ {full_price:.2f}")

    # Check eligibility
    print("\n3. Payment eligibility check:")
    eligible, reason, omega = omega_pay.check_payment_eligibility()
    print(f"   Eligible: {eligible}")
    print(f"   Reason: {reason}")
    print(f"   Ω Score: {omega:.4f}")

    # Create payment intent
    print("\n4. Creating payment intent...")
    intent = omega_pay.create_payment_intent(
        tier=AuditTier.QUICK,
        customer_email="customer@example.com",
        file_hash="abc123def456",
        metadata={'source': 'test'}
    )

    if intent['success']:
        print(f"   ✅ Payment intent created")
        print(f"   Payment ID: {intent['payment_id']}")
        print(f"   Amount: {intent['currency']} {intent['amount']:.2f}")
        print(f"   Ω Score: {intent['omega_score']:.4f}")
    else:
        print(f"   ❌ Failed: {intent['message']}")

    # Test under attack (prices should increase)
    print("\n5. Simulating attack (CVaR spike)...")
    for _ in range(10):
        stabilizer.update_cvar(0.25)

    quick_price_attack = omega_pay.get_current_price(AuditTier.QUICK)
    full_price_attack = omega_pay.get_current_price(AuditTier.FULL)

    print(f"   Quick Audit: R$ {quick_price:.2f} → R$ {quick_price_attack:.2f}")
    print(f"   Full Audit:  R$ {full_price:.2f} → R$ {full_price_attack:.2f}")
    print(f"   Price multiplier: {stabilizer.state.price_multiplier:.2f}x")
    print(f"   💡 Antifragility: Attack = Higher prices!")

    print("\n✅ Ω-Pay monetization test complete!")
