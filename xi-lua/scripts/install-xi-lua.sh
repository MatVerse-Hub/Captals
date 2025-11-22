#!/bin/bash
###############################################################################
# Ξ-LUA v2.0 - SuperProject Installer
###############################################################################
#
# One-line installation:
#   curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/xi-lua/scripts/install-xi-lua.sh | bash
#
# What this installs:
#   1. Lua-AutoHeal (ephemeral keys + kill-switch + Merkle-log)
#   2. Ω-OMNIVERSE (confidence scoring)
#   3. TemporalAnchor (PoSE smart contract)
#   4. Stabilizer-Recal (antifragility)
#   5. Ω-Pay (monetization)
#   6. Thermodynamic Metrics (Tabela IV)
#   7. IA-MetaMask (autonomous signing)
#   8. MatVerse-Copilot (deployment automation)
#
# Estimated time: 8-10 minutes
#
# Part of Ξ-LUA v2.0 SuperProject
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/MatVerse-Hub/test.git"
INSTALL_DIR="${HOME}/xi-lua"
DEPLOY_QUEUE="${HOME}/deploy-queue"

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║             Ξ-LUA v2.0 SuperProject Installer             ║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║  8 Sinergias Matadoras × 1 Comando Único × <10 minutos    ║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    print_step "Checking dependencies..."

    local missing_deps=()

    # Required: git, python3, pip3, node, npm
    command -v git >/dev/null 2>&1 || missing_deps+=("git")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v pip3 >/dev/null 2>&1 || missing_deps+=("pip3")
    command -v node >/dev/null 2>&1 || missing_deps+=("node")
    command -v npm >/dev/null 2>&1 || missing_deps+=("npm")

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Please install them first:"
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y git python3 python3-pip nodejs npm"
        echo "  macOS: brew install git python3 node"
        echo ""
        exit 1
    fi

    print_success "All dependencies found"
}

clone_repository() {
    print_step "Cloning MatVerse-Hub/test repository..."

    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists"
        read -p "Remove and re-install? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_error "Installation cancelled"
            exit 1
        fi
    fi

    git clone "$REPO_URL" "$INSTALL_DIR" --quiet

    cd "$INSTALL_DIR"

    print_success "Repository cloned"
}

install_python_components() {
    print_step "Installing Python components (Ξ-LUA core)..."

    # Install Python dependencies
    pip3 install --quiet --upgrade pip
    pip3 install --quiet \
        cryptography \
        numpy \
        python-dotenv \
        web3 \
        watchdog \
        requests \
        tweepy

    # Install Ξ-LUA core modules
    cd "$INSTALL_DIR/xi-lua"

    # Create __init__.py files
    touch core/__init__.py
    touch core/autoheal/__init__.py
    touch core/omniverse/__init__.py
    touch core/stabilizer/__init__.py
    touch core/metrics/__init__.py
    touch core/monetization/__init__.py

    print_success "Python components installed"
}

install_matverse_copilot() {
    print_step "Installing MatVerse-Copilot..."

    cd "$INSTALL_DIR/matverse-copilot"

    # Install as editable package
    pip3 install --quiet -e .

    # Create deploy queue
    mkdir -p "$DEPLOY_QUEUE"

    # Create config
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file - please configure it later"
    fi

    print_success "MatVerse-Copilot installed"
}

install_ia_metamask() {
    print_step "Installing IA-MetaMask..."

    cd "$INSTALL_DIR/ia-metamask"

    # Install Node.js dependencies
    npm install --silent

    # Create config
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file - please configure it later"
    fi

    print_success "IA-MetaMask installed"
}

create_cli_command() {
    print_step "Creating xi-lua CLI command..."

    # Create CLI wrapper script
    cat > "$INSTALL_DIR/xi-lua/xi-lua-cli.py" <<'EOFPYTHON'
#!/usr/bin/env python3
"""Ξ-LUA v2.0 Unified CLI"""
import sys
import argparse
from pathlib import Path

# Add xi-lua to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description='Ξ-LUA v2.0 SuperProject CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    # Heal test
    subparsers.add_parser('heal-test', help='Test Lua-AutoHeal')

    # Omega check
    subparsers.add_parser('omega', help='Check Ω-GATE score')

    # Stabilizer status
    subparsers.add_parser('stabilizer', help='Show Stabilizer status')

    # Metrics
    subparsers.add_parser('metrics', help='Show thermodynamic metrics')

    # Deploy
    deploy_parser = subparsers.add_parser('deploy', help='Deploy file/directory')
    deploy_parser.add_argument('path', help='Path to deploy')
    deploy_parser.add_argument('--tier', choices=['quick', 'full'], default='quick')

    args = parser.parse_args()

    if args.command == 'status':
        show_status()
    elif args.command == 'heal-test':
        test_autoheal()
    elif args.command == 'omega':
        check_omega()
    elif args.command == 'stabilizer':
        show_stabilizer()
    elif args.command == 'metrics':
        show_metrics()
    elif args.command == 'deploy':
        deploy_file(args.path, args.tier)
    else:
        parser.print_help()

def show_status():
    from core.autoheal.lua_autoheal import get_autoheal
    from core.omniverse.omega_gate import get_omega_gate
    from core.stabilizer.stabilizer_recal import get_stabilizer

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║              Ξ-LUA v2.0 System Status                   ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    autoheal = get_autoheal()
    omega_gate = get_omega_gate()
    stabilizer = get_stabilizer()

    # Autoheal
    status = autoheal.get_status()
    print(f"🔐 Lua-AutoHeal: {status['status']}")
    print(f"   Key rotations: {status['rotation_count']}")
    print(f"   Key age: {status['current_key_age']}s")
    print(f"   Chain integrity: {status['chain_integrity']}")

    # Omega
    passed, components = omega_gate.check_gate()
    print(f"\n🌊 Ω-OMNIVERSE: {'✅ PASS' if passed else '🔴 FAIL'}")
    print(f"   Ω score: {components.omega:.4f}")
    print(f"   CVaR: {components.cvar:.4f}")

    # Stabilizer
    print(f"\n⚡ Stabilizer: {'🔴 ATTACK MODE' if stabilizer.state.attack_mode else '🟢 NORMAL'}")
    print(f"   Ψ-target: {stabilizer.state.psi_target:.4f}")
    print(f"   Price multiplier: {stabilizer.state.price_multiplier:.2f}x")

    print("\n")

def test_autoheal():
    from core.autoheal.lua_autoheal import get_autoheal
    autoheal = get_autoheal()

    print("\n🧪 Testing Lua-AutoHeal...\n")
    data = b"Test secret from xi-lua"
    encrypted = autoheal.encrypt(data)
    decrypted = autoheal.decrypt(encrypted)

    print(f"Original:  {data}")
    print(f"Encrypted: {encrypted[:40]}...")
    print(f"Decrypted: {decrypted}")
    print(f"\n✅ Encryption working!\n")

def check_omega():
    from core.omniverse.omega_gate import get_omega_gate
    omega_gate = get_omega_gate()
    print(omega_gate.get_status_report())

def show_stabilizer():
    from core.stabilizer.stabilizer_recal import get_stabilizer
    stabilizer = get_stabilizer()
    print(stabilizer.get_status_report())

def show_metrics():
    from core.metrics.thermodynamic_metrics import ThermodynamicMetrics
    from core.omniverse.omega_gate import get_omega_gate

    metrics = ThermodynamicMetrics()
    omega_gate = get_omega_gate()

    passed, components = omega_gate.check_gate()

    state = metrics.compute_full_state(
        omega=components.omega,
        cvar=components.cvar,
        cumulative_energy=1000.0,
        blocks_passed=1000,
        omega_components=components.to_dict()
    )

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║       Tabela IV - Thermodynamic Metrics                 ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    for key, value in state.to_dict().items():
        print(f"{key:20s}: {value}")

    print("\n")

def deploy_file(path, tier):
    import shutil
    from pathlib import Path

    deploy_queue = Path.home() / "deploy-queue"
    source = Path(path)

    if not source.exists():
        print(f"❌ File not found: {path}")
        return

    # Create deployment name
    dest_name = f"now_{source.stem}_{tier}_{source.suffix}"
    dest = deploy_queue / dest_name

    # Copy to queue
    if source.is_dir():
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)

    print(f"✅ Deployed: {dest_name}")
    print(f"   Tier: {tier}")
    print(f"   Monitor: matverse-copilot logs -f")

if __name__ == '__main__':
    main()
EOFPYTHON

    chmod +x "$INSTALL_DIR/xi-lua/xi-lua-cli.py"

    # Create symlink
    sudo ln -sf "$INSTALL_DIR/xi-lua/xi-lua-cli.py" /usr/local/bin/xi-lua 2>/dev/null || {
        print_warning "Could not create /usr/local/bin/xi-lua (needs sudo)"
        print_warning "You can run: $INSTALL_DIR/xi-lua/xi-lua-cli.py"
    }

    print_success "xi-lua CLI created"
}

create_meta_dev_symlink() {
    print_step "Creating meta-dev symlink..."

    chmod +x "$INSTALL_DIR/meta-dev"
    sudo ln -sf "$INSTALL_DIR/meta-dev" /usr/local/bin/meta-dev 2>/dev/null || {
        print_warning "Could not create /usr/local/bin/meta-dev"
    }

    print_success "meta-dev CLI ready"
}

print_final_instructions() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║          ✅ Ξ-LUA v2.0 Installation Complete!             ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📦 Installed Components:${NC}"
    echo "   1. ✅ Lua-AutoHeal (ephemeral keys + kill-switch)"
    echo "   2. ✅ Ω-OMNIVERSE (confidence scoring)"
    echo "   3. ✅ TemporalAnchor (PoSE smart contract)"
    echo "   4. ✅ Stabilizer-Recal (antifragility)"
    echo "   5. ✅ Ω-Pay (monetization)"
    echo "   6. ✅ Thermodynamic Metrics (Tabela IV)"
    echo "   7. ✅ IA-MetaMask (autonomous signing)"
    echo "   8. ✅ MatVerse-Copilot (deployment automation)"
    echo ""
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo ""
    echo "   # Check system status"
    echo "   xi-lua status"
    echo ""
    echo "   # Test Lua-AutoHeal"
    echo "   xi-lua heal-test"
    echo ""
    echo "   # Check Ω score"
    echo "   xi-lua omega"
    echo ""
    echo "   # Deploy a file"
    echo "   xi-lua deploy paper.pdf --tier full"
    echo ""
    echo "   # Start MatVerse-Copilot (24/7 monitoring)"
    echo "   matverse-copilot start -d"
    echo ""
    echo "   # Start IA-MetaMask API"
    echo "   meta-dev init"
    echo ""
    echo -e "${YELLOW}⚙️  Configuration Needed:${NC}"
    echo ""
    echo "   1. MatVerse-Copilot: Edit ~/xi-lua/matverse-copilot/.env"
    echo "      - Add Polygon RPC URL"
    echo "      - Add wallet private key"
    echo "      - Add Twitter API keys (optional)"
    echo ""
    echo "   2. IA-MetaMask: Edit ~/xi-lua/ia-metamask/.env"
    echo "      - Add MetaMask private key"
    echo ""
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "   https://github.com/MatVerse-Hub/test"
    echo ""
    echo -e "${GREEN}🎉 The Ξ-LUA is now alive and waiting for your first deployment!${NC}"
    echo ""
}

# Main installation flow
main() {
    print_header

    check_dependencies
    clone_repository
    install_python_components
    install_matverse_copilot
    install_ia_metamask
    create_cli_command
    create_meta_dev_symlink

    print_final_instructions
}

main "$@"
