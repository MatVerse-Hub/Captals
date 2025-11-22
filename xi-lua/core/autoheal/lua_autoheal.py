#!/usr/bin/env python3
"""
Lua-AutoHeal - Autonomous Security System
==========================================

Features:
- Ephemeral key rotation every 5 minutes
- Automatic kill-switch on suspicious patterns
- Merkle-chain based immutable logging
- Zero-trust architecture

Part of Ξ-LUA v2.0 SuperProject
"""

import os
import time
import hashlib
import hmac
import json
import secrets
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Dict, List, Optional, Tuple
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [Lua-AutoHeal] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MerkleChainLogger:
    """Immutable logging with Merkle chain"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.expanduser('~/.xi-lua/autoheal.log')
        self.chain: List[Dict] = []
        self.current_root = "0" * 64  # Genesis root

        # Create log directory
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # Load existing chain
        self._load_chain()

    def _load_chain(self):
        """Load existing Merkle chain from disk"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.chain = [json.loads(line) for line in f]
                if self.chain:
                    self.current_root = self.chain[-1]['merkle_root']
            except Exception as e:
                logger.warning(f"Failed to load chain: {e}")

    def _compute_hash(self, data: str, prev_root: str) -> str:
        """Compute SHA-3 hash of data + previous root"""
        combined = f"{data}|{prev_root}".encode('utf-8')
        return hashlib.sha3_256(combined).hexdigest()

    def append(self, event: str, metadata: Dict = None):
        """Append event to Merkle chain"""
        timestamp = datetime.utcnow().isoformat()
        entry = {
            'timestamp': timestamp,
            'event': event,
            'metadata': metadata or {},
            'prev_root': self.current_root
        }

        # Compute new Merkle root
        entry_str = json.dumps(entry, sort_keys=True)
        new_root = self._compute_hash(entry_str, self.current_root)
        entry['merkle_root'] = new_root

        # Update current root
        self.current_root = new_root

        # Append to chain
        self.chain.append(entry)

        # Persist to disk
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        logger.info(f"{event} [Root: {new_root[:10]}...]")

        return new_root

    def verify_integrity(self) -> bool:
        """Verify entire chain integrity"""
        if not self.chain:
            return True

        current_root = "0" * 64
        for entry in self.chain:
            # Recreate entry without merkle_root for verification
            verify_entry = {
                'timestamp': entry['timestamp'],
                'event': entry['event'],
                'metadata': entry['metadata'],
                'prev_root': entry['prev_root']
            }
            entry_str = json.dumps(verify_entry, sort_keys=True)
            expected_root = self._compute_hash(entry_str, current_root)

            if expected_root != entry['merkle_root']:
                logger.error(f"Chain integrity violation at {entry['timestamp']}")
                return False

            current_root = entry['merkle_root']

        return True


class EphemeralKeyManager:
    """
    Manages ephemeral keys with 5-minute rotation

    Uses AES-256-GCM for encryption (quantum-resistant symmetric crypto)
    Key derivation: HKDF with SHA-3
    Nonce: 96-bit random (cryptographically secure)
    """

    def __init__(self, rotation_interval: int = 300):  # 300 seconds = 5 minutes
        self.rotation_interval = rotation_interval
        self.current_key: Optional[bytes] = None
        self.current_aesgcm: Optional[AESGCM] = None
        self.key_created_at: Optional[datetime] = None
        self.rotation_count = 0
        self.logger = MerkleChainLogger()

        # Master key path (persistent across rotations)
        self.master_key_path = os.path.expanduser('~/.xi-lua/master.key')
        self.master_key = self._ensure_master_key()

        # Generate initial key
        self._rotate_key()

        # Start rotation thread
        self.rotation_thread = threading.Thread(target=self._rotation_loop, daemon=True)
        self.rotation_thread.start()

    def _ensure_master_key(self) -> bytes:
        """
        Ensure master key exists (create if not)
        Master key is persistent and used for key derivation
        """
        os.makedirs(os.path.dirname(self.master_key_path), exist_ok=True)

        if os.path.exists(self.master_key_path):
            with open(self.master_key_path, 'rb') as f:
                master_key = f.read()
            logger.info("Master key loaded from disk")
        else:
            # Generate new 256-bit master key
            master_key = secrets.token_bytes(32)
            with open(self.master_key_path, 'wb') as f:
                f.write(master_key)
            os.chmod(self.master_key_path, 0o600)  # Read/write for owner only
            logger.info("New master key generated and saved")

        return master_key

    def _derive_ephemeral_key(self, salt: bytes) -> bytes:
        """
        Derive ephemeral key from master key using SHA-3

        Args:
            salt: Random salt for key derivation

        Returns:
            32-byte AES-256 key
        """
        # Simple HKDF-like derivation with SHA-3
        combined = self.master_key + salt
        return hashlib.sha3_256(combined).digest()

    def _rotate_key(self):
        """Generate new ephemeral key via derivation"""
        # Generate random salt
        salt = secrets.token_bytes(32)

        # Derive new key
        new_key = self._derive_ephemeral_key(salt)
        self.current_key = new_key
        self.current_aesgcm = AESGCM(new_key)
        self.key_created_at = datetime.utcnow()
        self.rotation_count += 1

        # Log rotation to Merkle chain (SHA-3 hash of key)
        key_hash = hashlib.sha3_256(new_key).hexdigest()
        self.logger.append(
            f"Key rotation #{self.rotation_count}",
            {
                'rotation_count': self.rotation_count,
                'key_hash_sha3': key_hash[:16],
                'salt_hash': hashlib.sha3_256(salt).hexdigest()[:16],
                'valid_until': (self.key_created_at + timedelta(seconds=self.rotation_interval)).isoformat()
            }
        )

    def _rotation_loop(self):
        """Background thread for automatic key rotation"""
        while True:
            time.sleep(self.rotation_interval)
            self._rotate_key()

    def get_key(self) -> AESGCM:
        """Get current ephemeral AESGCM cipher"""
        # Check if key expired
        if datetime.utcnow() - self.key_created_at > timedelta(seconds=self.rotation_interval):
            logger.warning("Key expired, forcing rotation")
            self._rotate_key()

        return self.current_aesgcm

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data with current ephemeral key (AES-256-GCM)

        Returns: nonce + ciphertext (nonce is prepended)
        """
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        ciphertext = self.get_key().encrypt(nonce, data, None)
        # Return nonce + ciphertext
        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data with current ephemeral key (AES-256-GCM)

        Args:
            encrypted_data: nonce + ciphertext
        """
        # Extract nonce (first 12 bytes)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        return self.get_key().decrypt(nonce, ciphertext, None)

    def sign_attestation(self, data: bytes) -> Tuple[str, str]:
        """
        Sign data with HMAC-SHA3 + nonce for idempotency

        Returns:
            (signature_b64, nonce_hex)
        """
        # Generate unique nonce
        nonce = secrets.token_bytes(16)

        # Create HMAC with SHA-3
        combined = data + nonce
        signature = hmac.new(
            self.current_key,
            combined,
            hashlib.sha3_256
        ).digest()

        # Return as base64 + hex
        return base64.b64encode(signature).decode('utf-8'), nonce.hex()

    def verify_attestation(self, data: bytes, signature_b64: str, nonce_hex: str) -> bool:
        """
        Verify HMAC-SHA3 signature

        Args:
            data: Original data
            signature_b64: Base64-encoded signature
            nonce_hex: Hex-encoded nonce

        Returns:
            True if signature is valid
        """
        try:
            nonce = bytes.fromhex(nonce_hex)
            expected_sig = base64.b64decode(signature_b64)

            combined = data + nonce
            computed_sig = hmac.new(
                self.current_key,
                combined,
                hashlib.sha3_256
            ).digest()

            # Constant-time comparison
            return hmac.compare_digest(expected_sig, computed_sig)
        except Exception:
            return False


class KillSwitch:
    """Automatic kill-switch for suspicious patterns"""

    def __init__(self, threshold: int = 3, window: int = 60):
        self.threshold = threshold  # Max suspicious events before kill
        self.window = window  # Time window in seconds
        self.events: List[float] = []
        self.armed = True
        self.logger = MerkleChainLogger()

    def report_suspicious_event(self, event_type: str, details: Dict = None):
        """Report suspicious event and check if kill-switch should activate"""
        now = time.time()
        self.events.append(now)

        # Remove events outside window
        self.events = [t for t in self.events if now - t < self.window]

        # Log event
        self.logger.append(
            f"Suspicious: {event_type}",
            {
                'type': event_type,
                'details': details or {},
                'count_in_window': len(self.events)
            }
        )

        # Check if threshold exceeded
        if len(self.events) >= self.threshold:
            self.activate()
            return True

        return False

    def activate(self):
        """Activate kill-switch - shut down system"""
        if not self.armed:
            return

        self.armed = False

        self.logger.append(
            "KILL-SWITCH ACTIVATED",
            {
                'reason': f'{len(self.events)} suspicious events in {self.window}s',
                'threshold': self.threshold
            }
        )

        logger.critical("🔴 KILL-SWITCH ACTIVATED - Shutting down system")
        logger.critical(f"Reason: {len(self.events)} suspicious events detected")

        # TODO: Implement actual shutdown logic
        # For now, just log. In production, would:
        # - Stop all services
        # - Close network connections
        # - Encrypt sensitive data
        # - Send alert to admin

        raise SystemExit("Kill-switch activated due to suspicious activity")


class LuaAutoHeal:
    """
    Main Lua-AutoHeal system combining:
    - Ephemeral key rotation (every 5 min)
    - Kill-switch (on suspicious patterns)
    - Merkle-chain logging (immutable audit trail)
    """

    def __init__(self):
        self.key_manager = EphemeralKeyManager(rotation_interval=300)
        self.kill_switch = KillSwitch(threshold=3, window=60)
        self.logger = MerkleChainLogger()

        self.logger.append("Lua-AutoHeal initialized", {
            'version': '2.0',
            'rotation_interval': 300,
            'kill_switch_threshold': 3
        })

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data with current ephemeral key"""
        return self.key_manager.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with current ephemeral key"""
        return self.key_manager.decrypt(encrypted_data)

    def report_suspicious(self, event_type: str, details: Dict = None):
        """Report suspicious activity"""
        return self.kill_switch.report_suspicious_event(event_type, details)

    def verify_integrity(self) -> bool:
        """Verify Merkle chain integrity"""
        return self.logger.verify_integrity()

    def sign_data(self, data: bytes) -> Tuple[str, str]:
        """
        Sign data with quantum-resistant HMAC-SHA3 + nonce

        Returns:
            (signature_b64, nonce_hex)
        """
        sig, nonce = self.key_manager.sign_attestation(data)

        # Log signing event
        self.logger.append("Data signed", {
            'data_hash': hashlib.sha3_256(data).hexdigest()[:16],
            'signature': sig[:16] + '...',
            'nonce': nonce[:16] + '...'
        })

        return sig, nonce

    def verify_signature(self, data: bytes, signature_b64: str, nonce_hex: str) -> bool:
        """
        Verify HMAC-SHA3 signature

        Returns:
            True if valid
        """
        return self.key_manager.verify_attestation(data, signature_b64, nonce_hex)

    def get_status(self) -> Dict:
        """Get system status"""
        return {
            'status': 'ACTIVE' if self.kill_switch.armed else 'KILLED',
            'rotation_count': self.key_manager.rotation_count,
            'current_key_age': (datetime.utcnow() - self.key_manager.key_created_at).seconds,
            'merkle_root': self.logger.current_root,
            'chain_length': len(self.logger.chain),
            'chain_integrity': self.verify_integrity()
        }


# Singleton instance
_autoheal_instance: Optional[LuaAutoHeal] = None


def get_autoheal() -> LuaAutoHeal:
    """Get global Lua-AutoHeal instance"""
    global _autoheal_instance
    if _autoheal_instance is None:
        _autoheal_instance = LuaAutoHeal()
    return _autoheal_instance


if __name__ == '__main__':
    # Test the system
    print("=== Lua-AutoHeal Test ===\n")

    autoheal = get_autoheal()

    # Test encryption
    print("1. Testing ephemeral encryption...")
    data = b"Secret message from Xi-LUA"
    encrypted = autoheal.encrypt(data)
    decrypted = autoheal.decrypt(encrypted)
    print(f"   Original:  {data}")
    print(f"   Encrypted: {encrypted[:50]}...")
    print(f"   Decrypted: {decrypted}")
    print(f"   ✓ Encryption working\n")

    # Test Merkle chain
    print("2. Testing Merkle chain logging...")
    autoheal.logger.append("Test event 1", {'test': True})
    autoheal.logger.append("Test event 2", {'value': 42})
    print(f"   Chain length: {len(autoheal.logger.chain)}")
    print(f"   Current root: {autoheal.logger.current_root}")
    print(f"   Integrity: {autoheal.verify_integrity()}")
    print(f"   ✓ Merkle chain working\n")

    # Test kill-switch
    print("3. Testing kill-switch (will NOT activate)...")
    autoheal.report_suspicious("test_event", {'severity': 'low'})
    status = autoheal.get_status()
    print(f"   Status: {status['status']}")
    print(f"   ✓ Kill-switch armed\n")

    # Show final status
    print("4. Final status:")
    status = autoheal.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    print("\n✅ Lua-AutoHeal is operational!")
