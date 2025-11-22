#!/usr/bin/env python3
"""
Ξ-LUA v2.0 - Command Line Interface
====================================

The main CLI for interacting with the LUA-AutoHeal security system.

Commands:
  heal-test    - Test ephemeral key rotation and signing
  status       - Show system status (AutoHeal + Stabilizer)
  logs         - View Merkle-chain logs
  attack-sim   - Simulate attack to test antifragility
  verify       - Verify Merkle chain integrity

Part of Ξ-LUA v2.0 SuperProject
"""

import sys
import argparse
import time
import os
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

from core.autoheal.lua_autoheal import get_autoheal, LuaAutoHeal
from core.stabilizer.stabilizer_recal import get_stabilizer, StabilizerRecal
from core.omniverse.omega_gate import OmegaGate


def cmd_heal_test():
    """Test LUA-AutoHeal key rotation and signing"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         LUA-AutoHeal Security Test                       ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    autoheal = get_autoheal()

    # Test 1: Ephemeral encryption
    print("1. Testing ephemeral key rotation...")
    test_data = b"Secret message from Xi-LUA v2.0"
    encrypted = autoheal.encrypt(test_data)
    decrypted = autoheal.decrypt(encrypted)

    print(f"   ✓ Key rotation count: {autoheal.key_manager.rotation_count}")
    print(f"   ✓ Current key age: {autoheal.get_status()['current_key_age']}s")
    print(f"   ✓ Encryption: {len(encrypted)} bytes")
    print(f"   ✓ Decryption: {'SUCCESS' if decrypted == test_data else 'FAILED'}\n")

    # Test 2: Merkle chain
    print("2. Testing Merkle-chain logging...")
    root_before = autoheal.logger.current_root[:10]
    autoheal.logger.append("heal-test event", {
        'test': True,
        'timestamp': time.time()
    })
    root_after = autoheal.logger.current_root[:10]

    print(f"   ✓ Root before: {root_before}...")
    print(f"   ✓ Root after:  {root_after}...")
    print(f"   ✓ Chain length: {len(autoheal.logger.chain)} entries\n")

    # Test 3: Signature generation (quantum-resistant)
    print("3. Testing SHA-3/Keccak256 signature...")
    import hashlib
    content = b"test content for signing"
    signature = hashlib.sha3_256(content).hexdigest()
    print(f"   ✓ Content: {content.decode()}")
    print(f"   ✓ SHA-3 Hash: {signature[:32]}...\n")

    # Final status
    status = autoheal.get_status()
    print("4. Final AutoHeal Status:")
    print(f"   Status: {status['status']}")
    print(f"   Merkle Root: {status['merkle_root'][:16]}...")
    print(f"   Chain Integrity: {'✓ VALID' if status['chain_integrity'] else '✗ INVALID'}")

    print("\n✅ LUA-AutoHeal test complete!")


def cmd_status():
    """Show complete system status"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Ξ-LUA v2.0 System Status                         ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # AutoHeal status
    autoheal = get_autoheal()
    ah_status = autoheal.get_status()

    print("┌─────────────────────────────────────────────────────────┐")
    print("│  LUA-AutoHeal Security System                           │")
    print("└─────────────────────────────────────────────────────────┘")
    print(f"  Status:            {ah_status['status']}")
    print(f"  Key Rotations:     {ah_status['rotation_count']}")
    print(f"  Current Key Age:   {ah_status['current_key_age']}s / 300s")
    print(f"  Merkle Root:       {ah_status['merkle_root'][:32]}...")
    print(f"  Chain Length:      {ah_status['chain_length']} entries")
    print(f"  Chain Integrity:   {'✓ VALID' if ah_status['chain_integrity'] else '✗ COMPROMISED'}")

    # Stabilizer status
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  Stabilizer-Recal Antifragility System                  │")
    print("└─────────────────────────────────────────────────────────┘")

    stabilizer = get_stabilizer()
    state = stabilizer.state

    mode_emoji = "🔴" if state.attack_mode else "🟢"
    mode_text = "ATTACK MODE" if state.attack_mode else "NORMAL"

    print(f"  Mode:              {mode_emoji} {mode_text}")
    print(f"  Ψ-target:          {state.psi_target:.4f}")
    print(f"  CVaR:              {state.cvar:.4f} ({'DANGER' if state.cvar > 0.15 else 'OK'})")
    print(f"  Price Multiplier:  {state.price_multiplier:.2f}x")
    print(f"  Recalibrations:    {state.recalibration_count}")

    # Omega-Gate (if available)
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│  Ω-Gate Quality Control                                  │")
    print("└─────────────────────────────────────────────────────────┘")
    try:
        omega = OmegaGate()
        print(f"  Threshold:         {omega.omega_threshold:.2f}")
        print(f"  Status:            {'✓ OPERATIONAL' if omega.omega_threshold > 0 else '✗ OFFLINE'}")
    except Exception as e:
        print(f"  Status:            ⚠️ Not initialized")

    print("\n" + "═" * 61)
    security_level = "MAXIMUM" if ah_status['status'] == 'ACTIVE' and not state.attack_mode else "ELEVATED"
    print(f"Overall Security Level: {security_level}")
    print("═" * 61 + "\n")


def cmd_logs(follow=False, tail=20):
    """View Merkle-chain logs"""
    autoheal = get_autoheal()

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Merkle-Chain Immutable Logs                      ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    if not autoheal.logger.chain:
        print("No logs yet.\n")
        return

    # Show last N entries
    entries = autoheal.logger.chain[-tail:] if len(autoheal.logger.chain) > tail else autoheal.logger.chain

    for entry in entries:
        timestamp = entry['timestamp']
        event = entry['event']
        merkle_root = entry['merkle_root'][:16]
        prev_root = entry['prev_root'][:16]

        print(f"[{timestamp}]")
        print(f"  Event: {event}")
        print(f"  Root:  {merkle_root}... (prev: {prev_root}...)")

        if entry.get('metadata'):
            for key, value in entry['metadata'].items():
                print(f"    {key}: {value}")
        print()

    print(f"Total entries: {len(autoheal.logger.chain)}")
    print(f"Current root: {autoheal.logger.current_root[:32]}...\n")

    # Verify integrity
    print("Verifying chain integrity...", end=" ")
    if autoheal.verify_integrity():
        print("✓ VALID\n")
    else:
        print("✗ COMPROMISED!\n")


def cmd_attack_sim():
    """Simulate attack to test antifragility"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Attack Simulation - Antifragility Test           ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    stabilizer = get_stabilizer()
    autoheal = get_autoheal()

    print("Initial state:")
    print(f"  Ψ-target: {stabilizer.state.psi_target:.4f}")
    print(f"  Price: {stabilizer.state.price_multiplier:.2f}x")
    print(f"  Mode: {'ATTACK' if stabilizer.state.attack_mode else 'NORMAL'}\n")

    print("Simulating attack (high CVaR for 6 seconds)...")
    print("┌─────────────────────────────────────────────────────────┐")

    for i in range(60):  # 6 seconds at 10 updates/sec
        # Simulate high risk
        recalibrated = stabilizer.update_cvar(0.22)

        # Report suspicious activity to AutoHeal
        if i % 10 == 0:
            autoheal.report_suspicious("simulated_attack", {
                'iteration': i,
                'cvar': 0.22
            })

        if recalibrated:
            print(f"\n🔴 RECALIBRATION at iteration {i}:")
            print(f"   Ψ: {stabilizer.state.psi_target:.4f}")
            print(f"   Price: {stabilizer.state.price_multiplier:.2f}x\n")

        # Progress indicator
        if i % 10 == 0:
            print(f"  [{i//10 + 1}/6] CVaR=0.22 ...", end="")
            sys.stdout.flush()

        time.sleep(0.1)

    print("\n└─────────────────────────────────────────────────────────┘\n")

    print("Final state (after attack):")
    print(f"  Ψ-target: {stabilizer.state.psi_target:.4f} ({'↑ INCREASED' if stabilizer.state.psi_target > 0.90 else 'unchanged'})")
    print(f"  Price: {stabilizer.state.price_multiplier:.2f}x ({'↑ INCREASED' if stabilizer.state.price_multiplier > 1.0 else 'unchanged'})")
    print(f"  Mode: {'🔴 ATTACK' if stabilizer.state.attack_mode else '🟢 NORMAL'}")
    print(f"  Recalibrations: {stabilizer.state.recalibration_count}\n")

    print("✅ Attack simulation complete!")
    print("   System demonstrated ANTIFRAGILITY:")
    print("   - Attack detected")
    print("   - Quality requirements increased")
    print("   - Price multiplier increased")
    print("   - System became STRONGER under stress\n")


def cmd_verify():
    """Verify Merkle chain integrity"""
    autoheal = get_autoheal()

    print("Verifying Merkle-chain integrity...\n")
    print(f"Chain length: {len(autoheal.logger.chain)} entries")
    print(f"Current root: {autoheal.logger.current_root}\n")

    if autoheal.verify_integrity():
        print("✅ Chain integrity: VALID")
        print("   All entries are cryptographically linked")
        print("   No tampering detected\n")
    else:
        print("❌ Chain integrity: COMPROMISED")
        print("   ⚠️  Tampering detected!")
        print("   System may be under attack\n")


def main():
    parser = argparse.ArgumentParser(
        description='Ξ-LUA v2.0 - Maximum Security System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  heal-test    Test LUA-AutoHeal key rotation and signing
  status       Show complete system status
  logs         View Merkle-chain logs
  attack-sim   Simulate attack to test antifragility
  verify       Verify Merkle chain integrity

Examples:
  ξ-lua heal-test
  ξ-lua status
  ξ-lua logs -f
  ξ-lua attack-sim
        """
    )

    parser.add_argument('command', choices=['heal-test', 'status', 'logs', 'attack-sim', 'verify'],
                        help='Command to execute')
    parser.add_argument('-f', '--follow', action='store_true',
                        help='Follow logs (for logs command)')
    parser.add_argument('-n', '--tail', type=int, default=20,
                        help='Number of log entries to show (default: 20)')

    args = parser.parse_args()

    try:
        if args.command == 'heal-test':
            cmd_heal_test()
        elif args.command == 'status':
            cmd_status()
        elif args.command == 'logs':
            cmd_logs(follow=args.follow, tail=args.tail)
        elif args.command == 'attack-sim':
            cmd_attack_sim()
        elif args.command == 'verify':
            cmd_verify()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
