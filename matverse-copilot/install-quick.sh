#!/bin/bash
#
# MatVerse-Copilot Quick Installer
# Installs and configures MatVerse-Copilot in 8-10 minutes
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
  __  __       ___      __
 |  \/  | __ _|_ _\    / /__ _ __ ___  ___
 | |\/| |/ _` || |____/ / _ \ '__/ __|/ _ \
 | |  | | (_| || |___/ /  __/ |  \__ \  __/
 |_|  |_|\__,_|___| /_/ \___|_|  |___/\___|

    🚀 MATVERSE-COPILOT INSTALLER v1.0

EOF
echo -e "${NC}"

echo -e "${GREEN}Starting installation...${NC}\n"

# Step 1: Check Python
echo -e "${BLUE}[1/8]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}\n"

# Step 2: Clone repository (if needed)
echo -e "${BLUE}[2/8]${NC} Setting up MatVerse-Copilot..."
INSTALL_DIR="$HOME/matverse-copilot"

if [ ! -d "$INSTALL_DIR" ]; then
    # Clone from GitHub
    if git clone https://github.com/MatVerse-Hub/test.git "$INSTALL_DIR" 2>/dev/null; then
        echo -e "${GREEN}✓ Repository cloned${NC}\n"
    else
        # If clone fails, create from current directory
        mkdir -p "$INSTALL_DIR"
        cp -r matverse-copilot/* "$INSTALL_DIR/" 2>/dev/null || true
        echo -e "${YELLOW}✓ Using local installation${NC}\n"
    fi
else
    echo -e "${YELLOW}✓ Directory already exists${NC}\n"
fi

cd "$INSTALL_DIR"

# Step 3: Install dependencies
echo -e "${BLUE}[3/8]${NC} Installing Python dependencies..."
pip3 install --user -e . --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Step 4: Create deploy queue directory
echo -e "${BLUE}[4/8]${NC} Creating deploy queue directory..."
QUEUE_DIR="$HOME/deploy-queue"
mkdir -p "$QUEUE_DIR"
mkdir -p "$QUEUE_DIR/processed"
echo -e "${GREEN}✓ Queue directory created at ${QUEUE_DIR}${NC}\n"

# Step 5: Configure environment
echo -e "${BLUE}[5/8]${NC} Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ .env file created. You need to configure it with your keys!${NC}"
    echo -e "${YELLOW}  Edit: ${INSTALL_DIR}/.env${NC}\n"
else
    echo -e "${GREEN}✓ .env already configured${NC}\n"
fi

# Step 6: Create systemd service (optional)
echo -e "${BLUE}[6/8]${NC} Setting up system service..."

SERVICE_FILE="$HOME/.config/systemd/user/matverse-copilot.service"
mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=MatVerse-Copilot Monitor
After=network.target

[Service]
Type=simple
ExecStart=$(which python3) -m src.monitor
WorkingDirectory=${INSTALL_DIR}
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo -e "${GREEN}✓ Systemd service created${NC}\n"

# Step 7: Add to PATH (if not already)
echo -e "${BLUE}[7/8]${NC} Adding to PATH..."

# Check if pip user bin is in PATH
USER_BIN="$HOME/.local/bin"
if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}✓ Added to PATH${NC}\n"
else
    echo -e "${GREEN}✓ Already in PATH${NC}\n"
fi

# Step 8: Final verification
echo -e "${BLUE}[8/8]${NC} Verifying installation..."

if command -v matverse-copilot &> /dev/null; then
    echo -e "${GREEN}✓ matverse-copilot command available${NC}\n"
else
    echo -e "${YELLOW}⚠ Command not found yet. Restart your terminal or run:${NC}"
    echo -e "${YELLOW}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
fi

# Installation complete
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}║  ✓ MatVerse-Copilot installed successfully!      ║${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Next steps:${NC}\n"
echo -e "${YELLOW}1. Configure your .env file:${NC}"
echo -e "   nano ${INSTALL_DIR}/.env\n"

echo -e "${YELLOW}2. Add your credentials:${NC}"
echo -e "   - Polygon RPC URL (default: https://rpc-amoy.polygon.technology/)"
echo -e "   - Wallet private key"
echo -e "   - Twitter API tokens"
echo -e "   - NFT contract address\n"

echo -e "${YELLOW}3. Start the monitor:${NC}"
echo -e "   matverse-copilot start -d\n"

echo -e "${YELLOW}4. Check status:${NC}"
echo -e "   matverse-copilot status\n"

echo -e "${YELLOW}5. Test NFT minting:${NC}"
echo -e "   cp test-image.png ~/deploy-queue/now_test_nft.png\n"

echo -e "${YELLOW}6. Test Twitter posting:${NC}"
echo -e "   echo \"Hello MatVerse! 🚀\" > ~/deploy-queue/now_tweet.txt\n"

echo -e "${CYAN}Useful commands:${NC}"
echo -e "   matverse-copilot status      ${GREEN}# View system status${NC}"
echo -e "   matverse-copilot logs -f     ${GREEN}# Follow logs${NC}"
echo -e "   matverse-copilot queue       ${GREEN}# View deployment queue${NC}"
echo -e "   matverse-copilot stop        ${GREEN}# Stop monitor${NC}"
echo -e "   matverse-copilot restart     ${GREEN}# Restart monitor${NC}\n"

echo -e "${GREEN}🎉 Ready to deploy! Visit: https://testnets.opensea.io${NC}\n"
