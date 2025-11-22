"""
LUA-PAY Service - Payment gateway integration
"""

import requests
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from web3 import Web3

from .web3_service import Web3Service


class LUAPayService:
    def __init__(self, api_key: str, secret: str, base_url: str = "https://api.lua-pay.com/v1"):
        self.api_key = api_key
        self.secret = secret
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_invoice(
        self,
        amount: float,
        currency: str = "USDT",
        description: str = "Omega Capitals Investment",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new payment invoice
        """
        callback_url = os.getenv("LUA_PAY_WEBHOOK_URL", "https://api.omega-capitals.com/api/payments/webhook")
        success_url = os.getenv("FRONTEND_URL", "https://omega-capitals.com") + "/payment/success"

        payload = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "callback_url": callback_url,
            "success_url": success_url,
            "metadata": metadata or {}
        }

        try:
            response = requests.post(
                f"{self.base_url}/invoices",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            invoice = response.json()

            # Sign invoice for verification
            signature = self._sign_data(str(invoice.get('id', '')))
            invoice['signature'] = signature

            return invoice

        except requests.RequestException as e:
            print(f"Error creating invoice: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }

    def verify_payment(self, invoice_id: str) -> Dict[str, Any]:
        """
        Verify payment status
        """
        try:
            response = requests.get(
                f"{self.base_url}/invoices/{invoice_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            return {
                "invoice_id": invoice_id,
                "status": data.get('status'),
                "confirmed": data.get('status') == 'confirmed',
                "amount": data.get('amount'),
                "currency": data.get('currency'),
                "payer_address": data.get('payer_address'),
                "metadata": data.get('metadata', {})
            }

        except requests.RequestException as e:
            print(f"Error verifying payment: {e}")
            return {
                "invoice_id": invoice_id,
                "status": "error",
                "confirmed": False,
                "error": str(e)
            }

    def process_payment_confirmation(
        self,
        invoice_data: Dict[str, Any],
        web3_service: Web3Service
    ) -> Dict[str, Any]:
        """
        Process confirmed payment and trigger blockchain actions
        """
        try:
            payer_address = invoice_data.get('payer_address')
            amount = invoice_data.get('amount')
            product_type = invoice_data.get('metadata', {}).get('product_type', 'OmegaFund')

            if not payer_address or not amount:
                raise ValueError("Missing required payment data")

            # Mint Evidence Note NFT
            evidence_hash = self._generate_evidence_hash(invoice_data)

            tx_hash = web3_service.mint_evidence_note(
                recipient=payer_address,
                evidence_hash=evidence_hash,
                amount=int(amount * 1e18),  # Convert to wei
                product_type=product_type
            )

            return {
                "success": True,
                "tx_hash": tx_hash,
                "evidence_hash": evidence_hash,
                "payer": payer_address,
                "amount": amount
            }

        except Exception as e:
            print(f"Error processing payment confirmation: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature for security
        """
        expected_signature = self._sign_data(str(payload))
        return hmac.compare_digest(signature, expected_signature)

    def _sign_data(self, data: str) -> str:
        """
        Sign data using HMAC-SHA256
        """
        return hmac.new(
            self.secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def _generate_evidence_hash(self, invoice_data: Dict[str, Any]) -> str:
        """
        Generate evidence hash for NFT
        """
        data_string = f"{invoice_data.get('id')}-{invoice_data.get('amount')}-{invoice_data.get('timestamp')}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    def get_payment_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get payment statistics for a date range
        """
        try:
            response = requests.get(
                f"{self.base_url}/stats",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"Error getting payment stats: {e}")
            return {
                "error": str(e),
                "total_amount": 0,
                "transaction_count": 0
            }
