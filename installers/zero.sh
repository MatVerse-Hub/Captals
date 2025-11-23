#!/usr/bin/env bash
# MatVerse Zero-Cost Installer v1.0.0
# Curl one-liner: curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero.sh | bash

set -euo pipefail
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🍒 MatVerse ZERO-COST Installer${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

if [[ "$OS" != "Linux" ]] || [[ "$ARCH" != "x86_64" ]]; then
    echo -e "${YELLOW}⚠️ Otimizado para Linux AMD64. Detectado: $OS $ARCH${NC}"
    echo "Continue mesmo assim? (y/N)"
    read -r response
    [[ "$response" =~ ^[Yy]$ ]] || exit 1
fi

# 0. Preflight checks
echo "📦 Instalando dependências base..."
sudo apt-get update -qq
sudo apt-get install -y curl unzip squashfs-tools docker.io python3-pip

# 1. Ollama + DeepSeek
echo "🧠 Instalando LLM local (Ollama + DeepSeek 1.3B)..."
if ! command -v ollama &> /dev/null; then
    curl -L https://github.com/jmorganca/ollama/releases/download/v0.3.0/ollama-linux-amd64 -o /tmp/ollama
    sudo install -m 755 /tmp/ollama /usr/local/bin/ollama
fi

ollama serve &> /tmp/ollama.log &
OLLAMA_PID=$!
sleep 5
ollama pull deepseek-coder:1.3b-q4_K_M
echo "✓ LLM local operacional (PID: $OLLAMA_PID)"

# 2. Qdrant
echo "💾 Instalando Qdrant (vector store)..."
docker rm -f qdrant 2>/dev/null || true
docker run -d --name qdrant \
    -p 6333:6333 \
    -v "$PWD/qdrant:/qdrant/storage" \
    qdrant/qdrant
echo "✓ Qdrant online (localhost:6333)"

# 3. Foundry + Anvil
echo "⛓️ Instalando Foundry (blockchain local)..."
if ! command -v anvil &> /dev/null; then
    curl -L https://foundry.paradigm.xyz | bash
    export PATH="$HOME/.foundry/bin:$PATH"
    foundryup
fi

anvil --accounts 20 --gas-price 0 --gas-limit 30000000 &> anvil.log &
ANVIL_PID=$!
echo "✓ Anvil rodando (PID: $ANVIL_PID, gas 0)"

# 4. rclone + TeraBox
echo "☁️ Configurando rclone (TeraBox)..."
if ! command -v rclone &> /dev/null; then
    curl https://rclone.org/install.sh | sudo bash
fi

mkdir -p ~/.config/rclone
if [ ! -f ~/.config/rclone/rclone.conf ]; then
    echo -e "${YELLOW}⚠️ Configure TeraBox:${NC}"
    echo "   TERABOX_USER: "
    read -r TERABOX_USER
    echo "   TERABOX_PASS: "
    read -rs TERABOX_PASS

    cat > ~/.config/rclone/rclone.conf <<EOF
[terabox]
type = webdav
url = https://dav.terabox.com
vendor = other
user = $TERABOX_USER
pass = $(rclone obscure "$TERABOX_PASS")
EOF
fi

mkdir -p ~/terabox
rclone mount terabox: ~/terabox --daemon --vfs-cache-mode writes
echo "✓ TeraBox montado em ~/terabox"

# 5. Dual-Brain Watcher
echo "👁️ Instalando Dual-Brain Watcher..."
pip3 install watchdog requests

# 6. Atalhos CLI
echo "🔧 Criando comandos CLI..."
mkdir -p ~/.local/bin
cat > ~/.local/bin/matverse <<'EOF'
#!/usr/bin/env bash
case "$1" in
  status)
    echo "🔍 Status do Sistema:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s http://localhost:6333/health && echo "✓ Qdrant: OK" || echo "✗ Qdrant: FAIL"
    curl -s http://localhost:8545 && echo "✓ Anvil: OK" || echo "✗ Anvil: FAIL"
    pgrep -f "ollama serve" && echo "✓ Ollama: OK" || echo "✗ Ollama: FAIL"
    mountpoint -q ~/terabox && echo "✓ TeraBox: OK" || echo "✗ TeraBox: FAIL"
    ;;
  shell)
    python3 -m http.server 8080 -d .
    ;;
  deploy)
    echo "🚀 Deploying MatVerse em :8080..."
    python3 -m http.server 8080 -d . &
    echo "Acesse: http://$(hostname -I | awk '{print $1}'):8080"
    ;;
  *)
    echo "Uso: matverse {status|shell|deploy}"
    ;;
esac
EOF
chmod +x ~/.local/bin/matverse

# Adiciona ao PATH se necessário
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# 7. Resumo final
echo ""
echo -e "${GREEN}✅ MatVerse Zero-Cost instalado!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Componentes ativos:"
echo "  🧠 LLM: Ollama (deepseek-coder 1.3B)"
echo "  💾 Vector: Qdrant (localhost:6333)"
echo "  ⛓️ Chain: Anvil (gas 0)"
echo "  ☁️ Storage: TeraBox (~/terabox)"
echo ""
echo "🔧 Comandos disponíveis:"
echo "  matverse status   # Health check"
echo "  matverse deploy   # Sobe em :8080"
echo ""
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Docs: https://github.com/MatVerse-Hub/test/blob/main/README.md"
echo "💬 Issues: https://github.com/MatVerse-Hub/test/issues"
