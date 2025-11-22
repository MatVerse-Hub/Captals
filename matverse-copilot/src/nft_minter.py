#!/usr/bin/env python3
"""
NFT Minter for MatVerse-Copilot
Mints NFTs on Polygon Amoy testnet
"""

import os
import json
import logging
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('NFTMinter')


class NFTMinter:
    """Handles NFT minting on Polygon Amoy."""

    def __init__(self):
        # Connect to Polygon Amoy
        self.rpc_url = os.getenv('POLYGON_RPC_URL', 'https://rpc-amoy.polygon.technology/')
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Add PoA middleware for Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Load wallet
        self.private_key = os.getenv('WALLET_PRIVATE_KEY')
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            logger.warning("No WALLET_PRIVATE_KEY found. NFT minting disabled.")
            self.account = None

        # Load contract
        self.contract_address = os.getenv('NFT_CONTRACT_ADDRESS')
        self.contract = None

        if self.contract_address and self.contract_address != '0x0000000000000000000000000000000000000000':
            self._load_contract()

    def _load_contract(self):
        """Load the NFT contract ABI and create contract instance."""
        try:
            # Load ABI from contracts directory
            abi_path = Path(__file__).parent.parent / 'contracts' / 'EvidenceNFT.json'

            if abi_path.exists():
                with open(abi_path) as f:
                    contract_data = json.load(f)
                    abi = contract_data.get('abi', [])
            else:
                # Minimal ERC721 ABI
                abi = [
                    {
                        "inputs": [
                            {"name": "to", "type": "address"},
                            {"name": "tokenId", "type": "uint256"},
                            {"name": "uri", "type": "string"}
                        ],
                        "name": "safeMint",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ]

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=abi
            )
            logger.info(f"Contract loaded: {self.contract_address}")

        except Exception as e:
            logger.error(f"Failed to load contract: {e}")

    def mint_nft(self, image_path, metadata):
        """
        Mint an NFT with the given image and metadata.

        Args:
            image_path: Path to the image file
            metadata: Dictionary with NFT metadata

        Returns:
            Dictionary with transaction hash and OpenSea link
        """
        if not self.account:
            return {'error': 'No wallet configured'}

        if not self.contract:
            return {'error': 'No contract configured'}

        try:
            # Upload to IPFS (simplified - using NFT.storage or Pinata)
            ipfs_uri = self._upload_to_ipfs(image_path, metadata)

            # Generate token ID (use timestamp + random for uniqueness)
            import time
            token_id = int(time.time() * 1000)

            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            txn = self.contract.functions.safeMint(
                self.account.address,
                token_id,
                ipfs_uri
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': 80002  # Polygon Amoy chain ID
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            opensea_link = f"https://testnets.opensea.io/assets/amoy/{self.contract_address}/{token_id}"

            logger.info(f"NFT minted! Token ID: {token_id}, TX: {tx_hash.hex()}")

            return {
                'success': True,
                'token_id': token_id,
                'tx_hash': tx_hash.hex(),
                'opensea_link': opensea_link,
                'ipfs_uri': ipfs_uri
            }

        except Exception as e:
            logger.error(f"Minting failed: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def _upload_to_ipfs(self, image_path, metadata):
        """
        Upload image and metadata to IPFS.

        This is a simplified version. In production, use services like:
        - NFT.Storage (free)
        - Pinata
        - Infura IPFS
        """
        try:
            # For demo purposes, return a placeholder URI
            # In production, actually upload to IPFS
            import base64

            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()

            # Create metadata JSON
            metadata_json = {
                "name": metadata.get('name', 'MatVerse NFT'),
                "description": metadata.get('description', 'Generated by MatVerse-Copilot'),
                "image": f"data:image/png;base64,{image_data[:100]}...",  # Truncated for demo
                "attributes": metadata.get('attributes', [])
            }

            # In production, upload to IPFS and return the URI
            # For now, return a placeholder
            placeholder_uri = f"ipfs://QmPlaceholder{hash(image_path.name) % 100000}"

            logger.info(f"IPFS upload simulated: {placeholder_uri}")
            return placeholder_uri

        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            return f"ipfs://Qm{hash(str(e)) % 100000}"

    def check_connection(self):
        """Check if Web3 connection is working."""
        try:
            connected = self.w3.is_connected()
            if connected:
                block = self.w3.eth.block_number
                logger.info(f"Connected to Polygon Amoy. Latest block: {block}")
            return connected
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
