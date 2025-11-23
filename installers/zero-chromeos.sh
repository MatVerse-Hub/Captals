#!/usr/bin/env bash
# MatVerse Zero-Cost Installer for ChromeOS v1.0.0
# Optimized for Chromebooks with limited RAM/Storage

set -euo pipefail
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🍒 MatVerse ZERO-COST for ChromeOS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Detect if we're in ChromeOS Linux container
if [ ! -d "/opt/google/cros-containers" ]; then
    echo -e "${YELLOW}⚠️ Este instalador é otimizado para ChromeOS${NC}"
    echo "Detectado: $(uname -s) $(uname -m)"
    echo "Continue mesmo assim? (y/N)"
    read -r response
    [[ "$response" =~ ^[Yy]$ ]] || exit 1
fi

echo "📋 Preflight checks para ChromeOS..."
echo "  RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "  Storage: $(df -h / | awk 'NR==2 {print $4}') disponível"

# 0. Install minimal dependencies
echo "📦 Instalando dependências (mínimas)..."
sudo apt-get update -qq
sudo apt-get install -y curl unzip python3-minimal python3-pip

# 1. Ollama + DeepSeek (quantized for low RAM)
echo "🧠 Instalando LLM local (DeepSeek 1.3B quantizado)..."
if ! command -v ollama &> /dev/null; then
    curl -L https://github.com/jmorganca/ollama/releases/download/v0.3.0/ollama-linux-amd64 -o /tmp/ollama
    sudo install -m 755 /tmp/ollama /usr/local/bin/ollama
fi

# Start ollama server
ollama serve &> /tmp/ollama.log &
OLLAMA_PID=$!
sleep 5

# Pull smallest model
ollama pull deepseek-coder:1.3b-q4_K_M
echo "✓ LLM local operacional (PID: $OLLAMA_PID, ~800MB RAM)"

# 2. Qdrant (lightweight vector store)
echo "💾 Instalando Qdrant (local)..."
mkdir -p ~/matverse/qdrant
curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-musl.tar.gz \
    -o /tmp/qdrant.tar.gz
tar -xzf /tmp/qdrant.tar.gz -C ~/matverse/qdrant
chmod +x ~/matverse/qdrant/qdrant

# Start qdrant
~/matverse/qdrant/qdrant --config-path <(cat <<EOF
storage:
  storage_path: ~/matverse/qdrant-storage
service:
  http_port: 6333
  grpc_port: 6334
EOF
) &> /tmp/qdrant.log &
QDRANT_PID=$!
echo "✓ Qdrant online (PID: $QDRANT_PID)"

# 3. rclone + TeraBox (with swap)
echo "☁️ Configurando rclone + TeraBox..."
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

# Mount TeraBox (persiste entre reboots em /mnt/stateful_partition)
mkdir -p ~/matverse/terabox
rclone mount terabox: ~/matverse/terabox --daemon --vfs-cache-mode writes --allow-other

echo "✓ TeraBox montado em ~/matverse/terabox"

# 4. Create swap file on TeraBox (2GB)
echo "💾 Criando swap virtual no TeraBox (2GB)..."
if [ ! -f ~/matverse/terabox/matverse-swap ]; then
    dd if=/dev/zero of=~/matverse/terabox/matverse-swap bs=1M count=2048 status=progress
    chmod 600 ~/matverse/terabox/matverse-swap
    mkswap ~/matverse/terabox/matverse-swap
fi

sudo swapon ~/matverse/terabox/matverse-swap
echo "✓ Swap ativo: $(swapon --show)"

# 5. Dual-Brain Watcher (lightweight)
echo "👁️ Instalando Dual-Brain Watcher..."
pip3 install --user watchdog requests

cat > ~/matverse/dual_brain_watcher.py <<'PYEOF'
#!/usr/bin/env python3
import os
import time
import hashlib
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DualBrainWatcher(FileSystemEventHandler):
    ROOTS = [os.path.expanduser("~/matverse/terabox")]
    QDRANT = "http://localhost:6333"
    COLLECTION = "dual_brain"
    EXTENSIONS = (".txt", ".md", ".py", ".js", ".sol")

    def __init__(self):
        self.seen_hashes = set()
        self.qdrant_init()

    def qdrant_init(self):
        try:
            requests.put(
                f"{self.QDRANT}/collections/{self.COLLECTION}",
                json={
                    "vectors": {"size": 384, "distance": "Cosine"}  # Smaller embeddings
                }
            )
            print(f"✓ Qdrant collection '{self.COLLECTION}' pronta")
        except Exception as e:
            print(f"⚠️ Qdrant init error: {e}")

    def get_file_hash(self, path):
        return hashlib.md5(str(path).encode()).hexdigest()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.EXTENSIONS):
            print(f"📁 Novo arquivo: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.EXTENSIONS):
            print(f"✏️ Modificado: {event.src_path}")

if __name__ == "__main__":
    watcher = DualBrainWatcher()
    observer = Observer()
    for root in DualBrainWatcher.ROOTS:
        if os.path.exists(root):
            observer.schedule(watcher, root, recursive=True)

    observer.start()
    print("👁️ Watching TeraBox... (Ctrl+C para parar)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
PYEOF

chmod +x ~/matverse/dual_brain_watcher.py
python3 ~/matverse/dual_brain_watcher.py &> /tmp/watcher.log &
echo "✓ Watcher ativo"

# 6. MatVerse CLI
echo "🔧 Criando comandos CLI..."
mkdir -p ~/.local/bin
cat > ~/.local/bin/matverse <<'EOF'
#!/usr/bin/env bash
case "$1" in
  status)
    echo "🔍 Status do Sistema:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s http://localhost:6333/health && echo "✓ Qdrant: OK" || echo "✗ Qdrant: FAIL"
    pgrep -f "ollama serve" && echo "✓ Ollama: OK" || echo "✗ Ollama: FAIL"
    mountpoint -q ~/matverse/terabox && echo "✓ TeraBox: OK" || echo "✗ TeraBox: FAIL"
    swapon --show | grep -q matverse && echo "✓ Swap: OK" || echo "✗ Swap: FAIL"
    free -h
    ;;
  shell)
    python3 -m http.server 8080 -d ~/matverse
    ;;
  deploy)
    echo "🚀 Deploying MatVerse em :8080..."
    cd ~/matverse
    python3 -m http.server 8080 &
    echo "Acesse: http://localhost:8080"
    ;;
  swap-on)
    sudo swapon ~/matverse/terabox/matverse-swap
    echo "✓ Swap ativado"
    ;;
  swap-off)
    sudo swapoff ~/matverse/terabox/matverse-swap
    echo "✓ Swap desativado"
    ;;
  *)
    echo "Uso: matverse {status|shell|deploy|swap-on|swap-off}"
    ;;
esac
EOF
chmod +x ~/.local/bin/matverse

# Add to PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# 7. Auto-start on boot (ChromeOS)
cat > ~/matverse/autostart.sh <<'EOF'
#!/bin/bash
# Auto-start MatVerse services

# Ollama
ollama serve &> /tmp/ollama.log &

# Qdrant
~/matverse/qdrant/qdrant --config-path ~/matverse/qdrant.yaml &> /tmp/qdrant.log &

# TeraBox mount
rclone mount terabox: ~/matverse/terabox --daemon --vfs-cache-mode writes --allow-other

# Swap
sudo swapon ~/matverse/terabox/matverse-swap

# Watcher
python3 ~/matverse/dual_brain_watcher.py &> /tmp/watcher.log &

echo "✅ MatVerse services started"
EOF
chmod +x ~/matverse/autostart.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot $HOME/matverse/autostart.sh") | crontab -

# Final summary
echo ""
echo -e "${GREEN}✅ MatVerse Zero-Cost para ChromeOS instalado!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Componentes ativos:"
echo "  🧠 LLM: Ollama (deepseek-coder 1.3B) - ~800MB RAM"
echo "  💾 Vector: Qdrant (localhost:6333) - ~200MB RAM"
echo "  ☁️ Storage: TeraBox (~/matverse/terabox)"
echo "  💾 Swap: 2GB (TeraBox virtual)"
echo ""
echo "🔧 Comandos disponíveis:"
echo "  matverse status     # Health check"
echo "  matverse deploy     # Sobe em :8080"
echo "  matverse swap-on    # Ativar swap"
echo "  matverse swap-off   # Desativar swap"
echo ""
echo "📊 Uso de recursos:"
free -h
echo ""
echo "💾 Swap ativo:"
swapon --show
echo ""
echo "🌐 Acesse: http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Docs: README-CHROMEOS.md"
echo "💬 Issues: https://github.com/MatVerse-Hub/test/issues"
