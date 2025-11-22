#!/bin/bash
###############################################################################
# IA-MetaMask Quick Installer
# One-command installation for Chromebook/Linux
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/ia-metamask/install-quick.sh | bash
#
# Or:
#   bash install-quick.sh
#
# Author: MatVerse Hub
# License: MIT
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_color() {
  local color=$1
  shift
  echo -e "${color}$@${NC}"
}

print_header() {
  echo ""
  print_color "$CYAN" "╔════════════════════════════════════════════════════════════╗"
  print_color "$CYAN" "║      🤖 IA-MetaMask - Autonomous MetaMask AI Installer    ║"
  print_color "$CYAN" "╚════════════════════════════════════════════════════════════╝"
  echo ""
}

print_step() {
  print_color "$BLUE" "▶ $@"
}

print_success() {
  print_color "$GREEN" "✅ $@"
}

print_warning() {
  print_color "$YELLOW" "⚠️  $@"
}

print_error() {
  print_color "$RED" "❌ $@"
}

# Check if running on Chromebook/Linux
check_system() {
  print_step "Checking system requirements..."

  if ! command -v node &> /dev/null; then
    print_error "Node.js not found"
    print_warning "Install Node.js ≥ 18.0.0 first:"
    print_warning "  https://nodejs.org/"
    exit 1
  fi

  local node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
  if [ "$node_version" -lt 18 ]; then
    print_error "Node.js version too old: $(node --version)"
    print_warning "Requires Node.js ≥ 18.0.0"
    exit 1
  fi

  print_success "Node.js $(node --version) found"

  if ! command -v npm &> /dev/null; then
    print_error "npm not found"
    exit 1
  fi

  print_success "npm $(npm --version) found"
  echo ""
}

# Install IA-MetaMask
install_ia_metamask() {
  print_step "Installing IA-MetaMask..."
  echo ""

  local install_dir="${HOME}/ia-metamask"

  # Clone or update repository
  if [ -d "$install_dir" ]; then
    print_warning "IA-MetaMask already exists at $install_dir"
    read -p "Reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      print_warning "Installation cancelled"
      exit 0
    fi
    rm -rf "$install_dir"
  fi

  print_step "Cloning repository..."
  git clone https://github.com/MatVerse-Hub/test.git "$install_dir.tmp" 2>&1 | grep -v "Cloning into" || true
  mv "$install_dir.tmp/ia-metamask" "$install_dir"
  rm -rf "$install_dir.tmp"
  print_success "Repository cloned"
  echo ""

  # Install dependencies
  print_step "Installing Node.js dependencies (this may take 30-60 seconds)..."
  cd "$install_dir"
  npm install --silent --no-progress 2>&1 | grep -v "npm WARN" || true
  print_success "Dependencies installed"
  echo ""

  # Setup environment
  if [ ! -f "$install_dir/.env" ]; then
    print_step "Creating .env configuration..."
    cp "$install_dir/.env.example" "$install_dir/.env"
    print_success ".env file created"
    echo ""
  else
    print_warning ".env file already exists (keeping existing configuration)"
    echo ""
  fi
}

# Setup meta-dev CLI
install_meta_dev() {
  print_step "Installing meta-dev CLI..."
  echo ""

  local meta_dev_source="${HOME}/ia-metamask/../meta-dev"
  local meta_dev_target="/usr/local/bin/meta-dev"

  if [ -f "$meta_dev_source" ]; then
    if command -v sudo &> /dev/null; then
      sudo cp "$meta_dev_source" "$meta_dev_target" 2>/dev/null || {
        print_warning "Could not install to /usr/local/bin (no sudo access)"
        print_warning "Installing to ~/.local/bin instead"
        mkdir -p "$HOME/.local/bin"
        cp "$meta_dev_source" "$HOME/.local/bin/meta-dev"
        chmod +x "$HOME/.local/bin/meta-dev"

        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
          echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
          print_warning "Added ~/.local/bin to PATH in ~/.bashrc"
          print_warning "Run: source ~/.bashrc"
        fi
        print_success "meta-dev installed to ~/.local/bin/meta-dev"
      }
      if [ -f "$meta_dev_target" ]; then
        sudo chmod +x "$meta_dev_target"
        print_success "meta-dev installed to /usr/local/bin/meta-dev"
      fi
    else
      print_warning "sudo not available, installing to ~/.local/bin"
      mkdir -p "$HOME/.local/bin"
      cp "$meta_dev_source" "$HOME/.local/bin/meta-dev"
      chmod +x "$HOME/.local/bin/meta-dev"
      print_success "meta-dev installed to ~/.local/bin/meta-dev"
    fi
  else
    print_warning "meta-dev script not found (skipping CLI installation)"
  fi
  echo ""
}

# Configure private key
configure_private_key() {
  print_step "Configuration required"
  echo ""

  print_color "$CYAN" "You need to configure your MetaMask private key."
  print_color "$YELLOW" ""
  print_color "$YELLOW" "SECURITY WARNING:"
  print_color "$YELLOW" "  - Use a DEDICATED TESTNET WALLET (Polygon Amoy)"
  print_color "$YELLOW" "  - NEVER use your main wallet"
  print_color "$YELLOW" "  - Keep only small amounts for gas fees"
  print_color "$YELLOW" ""

  read -p "Do you want to configure now? (y/N): " -n 1 -r
  echo

  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_step "Steps to get your private key:"
    print_color "$CYAN" "  1. Open MetaMask browser extension"
    print_color "$CYAN" "  2. Click account menu → Account details"
    print_color "$CYAN" "  3. Click 'Show private key'"
    print_color "$CYAN" "  4. Enter your password"
    print_color "$CYAN" "  5. Copy the private key (without 0x prefix)"
    echo ""

    read -p "Paste your private key (input hidden): " -s private_key
    echo ""

    # Remove 0x prefix if present
    private_key="${private_key#0x}"

    # Validate (basic check for 64 hex characters)
    if [[ ! $private_key =~ ^[0-9a-fA-F]{64}$ ]]; then
      print_error "Invalid private key format"
      print_warning "Should be 64 hexadecimal characters (without 0x)"
      print_warning "You can configure later by editing: $HOME/ia-metamask/.env"
      return
    fi

    # Update .env file
    sed -i "s/PRIVATE_KEY=.*/PRIVATE_KEY=$private_key/" "$HOME/ia-metamask/.env"
    print_success "Private key configured"
    echo ""
  else
    print_warning "Skipping private key configuration"
    print_color "$CYAN" "Configure later by editing: $HOME/ia-metamask/.env"
    echo ""
  fi
}

# Print final instructions
print_final_instructions() {
  print_header
  print_success "IA-MetaMask installed successfully!"
  echo ""

  print_color "$CYAN" "📍 Installation directory: $HOME/ia-metamask"
  echo ""

  print_color "$CYAN" "🚀 Quick Start:"
  echo ""

  # Check if .env is configured
  if grep -q "your_metamask_private_key" "$HOME/ia-metamask/.env" 2>/dev/null; then
    print_color "$YELLOW" "1. Configure your private key:"
    print_color "$YELLOW" "   nano $HOME/ia-metamask/.env"
    print_color "$YELLOW" "   (Replace PRIVATE_KEY with your MetaMask key)"
    echo ""
  fi

  print_color "$GREEN" "2. Start IA-MetaMask (choose one):"
  echo ""
  print_color "$GREEN" "   WalletConnect Mode (mobile):"
  print_color "$GREEN" "   cd $HOME/ia-metamask && node ia-metamask.js"
  echo ""
  print_color "$GREEN" "   API Server Mode (automation):"
  print_color "$GREEN" "   cd $HOME/ia-metamask && node api-server.js"
  echo ""
  print_color "$GREEN" "   Or use meta-dev wrapper:"
  print_color "$GREEN" "   meta-dev init"
  echo ""

  print_color "$CYAN" "3. Test it:"
  print_color "$CYAN" "   curl http://localhost:3001/status"
  echo ""

  print_color "$CYAN" "📚 Documentation:"
  print_color "$CYAN" "   cat $HOME/ia-metamask/README.md"
  echo ""

  print_color "$CYAN" "💡 Examples:"
  print_color "$CYAN" "   meta-dev repo my-project    # Deploy repo + mint NFT"
  print_color "$CYAN" "   meta-dev paper paper.pdf    # Deploy paper + DOI + NFT"
  print_color "$CYAN" "   meta-dev nft image.png      # Mint NFT"
  echo ""

  print_color "$GREEN" "✨ Your MetaMask is ready to become an autonomous AI!"
  echo ""
}

# Main installation flow
main() {
  print_header

  check_system
  install_ia_metamask
  install_meta_dev
  configure_private_key
  print_final_instructions
}

# Run installer
main "$@"
