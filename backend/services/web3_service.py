"""
Web3 Service - Blockchain interaction layer
"""

from web3 import Web3
from eth_account import Account
import json
import os
from typing import Dict, Any, Optional


class Web3Service:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key:
            self.account = Account.from_key(self.private_key)
        else:
            self.account = None

    def calculate_omega_score(self, asset_address: str) -> int:
        """
        Calculate Omega Score for an asset by calling the smart contract
        """
        try:
            # Load contract ABI (simplified version)
            omega_contract_address = os.getenv("OMEGA_CONTRACT_ADDRESS")
            if not omega_contract_address:
                return 0

            # In production, load actual ABI from file
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(omega_contract_address),
                abi=[{
                    "inputs": [{"name": "asset", "type": "address"}],
                    "name": "getOmegaScore",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )

            score = contract.functions.getOmegaScore(
                Web3.to_checksum_address(asset_address)
            ).call()

            return score

        except Exception as e:
            print(f"Error calculating Omega Score: {e}")
            return 0

    def get_pool_reserves(self, pool_address: str) -> Dict[str, int]:
        """
        Get reserves from an Omega Pool
        """
        try:
            pool_abi = [{
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"name": "_reserveA", "type": "uint256"},
                    {"name": "_reserveB", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }]

            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pool_address),
                abi=pool_abi
            )

            reserves = contract.functions.getReserves().call()

            return {
                "reserveA": reserves[0],
                "reserveB": reserves[1]
            }

        except Exception as e:
            print(f"Error getting pool reserves: {e}")
            return {"reserveA": 0, "reserveB": 0}

    def get_fund_metrics(self, fund_address: str) -> Dict[str, Any]:
        """
        Get metrics from an Omega Fund
        """
        try:
            fund_abi = [{
                "inputs": [],
                "name": "getFundMetrics",
                "outputs": [
                    {"name": "_totalAUM", "type": "uint256"},
                    {"name": "_navPerShare", "type": "uint256"},
                    {"name": "_totalShares", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }]

            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(fund_address),
                abi=fund_abi
            )

            metrics = contract.functions.getFundMetrics().call()

            return {
                "totalAUM": metrics[0],
                "navPerShare": metrics[1],
                "totalShares": metrics[2]
            }

        except Exception as e:
            print(f"Error getting fund metrics: {e}")
            return {
                "totalAUM": 0,
                "navPerShare": 0,
                "totalShares": 0
            }

    def mint_evidence_note(
        self,
        recipient: str,
        evidence_hash: str,
        amount: int,
        product_type: str
    ) -> Optional[str]:
        """
        Mint an Evidence Note NFT
        """
        try:
            if not self.account:
                raise Exception("No private key configured")

            evidence_contract_address = os.getenv("EVIDENCE_CONTRACT_ADDRESS")
            if not evidence_contract_address:
                raise Exception("Evidence contract not configured")

            # Simplified ABI
            abi = [{
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "evidenceHash", "type": "string"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "productType", "type": "string"}
                ],
                "name": "mintEvidenceNote",
                "outputs": [{"name": "tokenId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }]

            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(evidence_contract_address),
                abi=abi
            )

            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price

            transaction = contract.functions.mintEvidenceNote(
                Web3.to_checksum_address(recipient),
                evidence_hash,
                amount,
                product_type
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,
                'gasPrice': gas_price,
                'nonce': nonce
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.private_key
            )

            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            return tx_hash.hex()

        except Exception as e:
            print(f"Error minting Evidence Note: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            print(f"Error getting transaction receipt: {e}")
            return None
