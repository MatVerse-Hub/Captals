# 🍒 MatVerseOS - Complete Guide

## Sistema Operacional Web3 Portátil

---

## 🌐 Versões Disponíveis

### 1. **Versão Online** (Produção)
**URL**: https://mat-verse-os-7363c48f.base44.app
- ✅ Hospedado em Base44
- ✅ Acessível via browser
- ✅ Atualizado automaticamente

### 2. **Versão Local** (Portátil)
**Arquivo**: `matverse-os.html` (30KB)
- ✅ Single-file, zero dependências
- ✅ Funciona offline
- ✅ Bootável de USB/pendrive

---

## 📦 Features (Versão Local)

### 💬 LLM Chat
```javascript
// Conecta ao Ollama local
http://localhost:11434/api/generate

Model: deepseek-coder:1.3b-q4_K_M
Cost: $0/mês
Privacy: 100% local
```

### 🔍 Vector Search
```javascript
// Busca semântica via Qdrant
http://localhost:6333/collections/dual_brain/points/search

Storage: TeraBox + Google Drive
Embeddings: 1536 dims
Deduplicação: Hash MD5
```

### ⛓️ Blockchain Explorer
```javascript
// Anvil local chain
http://localhost:8545

Gas: 0 gwei
Accounts: 20 pre-funded
Speed: Instant blocks
```

### 📁 File Manager (Dual-Brain)
```javascript
// Unified view
/mnt/terabox  → TeraBox (1TB free)
/mnt/gdrive   → Google Drive

Sync: Real-time
Indexing: Automatic
```

### 💻 Web Terminal
```bash
# Comandos disponíveis
help     - Lista comandos
status   - Status dos serviços
ls       - Lista arquivos
clear    - Limpa terminal
```

### 📊 System Monitor
```javascript
// Métricas em tempo real
CPU, RAM, Storage, Network

Update: A cada 2s
Charts: Visual dashboards
```

---

## 🚀 Quick Start

### Opção 1: Online (Imediato)
```
Abra: https://mat-verse-os-7363c48f.base44.app
```

### Opção 2: Local (Download)
```bash
# 1. Clone o repositório
git clone https://github.com/MatVerse-Hub/test.git
cd test

# 2. Abra o arquivo
open matverse-os.html
# ou
firefox matverse-os.html
# ou
chrome matverse-os.html
```

### Opção 3: ChromeOS (Zero-Cost Pack)
```bash
# 1. Habilitar Linux
Settings → Developers → Linux (Beta) → Turn On

# 2. Instalar pack completo
curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero-chromeos.sh | bash

# 3. Abrir MatVerseOS
matverse deploy
```

---

## ⚙️ Configuração de Serviços

Para usar todas as features da versão local:

### 1. Ollama (LLM)
```bash
# Instalar
curl https://ollama.ai/install.sh | sh

# Iniciar servidor
ollama serve

# Baixar modelo
ollama pull deepseek-coder:1.3b-q4_K_M

# Testar
curl http://localhost:11434/api/version
```

### 2. Qdrant (Vector DB)
```bash
# Via Docker
docker run -d -p 6333:6333 \
  -v $(pwd)/qdrant:/qdrant/storage \
  qdrant/qdrant

# Testar
curl http://localhost:6333/health
```

### 3. Anvil (Blockchain)
```bash
# Instalar Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Iniciar Anvil
anvil --accounts 20 --gas-price 0

# Testar
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### 4. TeraBox + Google Drive (Dual-Brain)
```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar TeraBox
rclone config
# Escolha: WebDAV
# URL: https://dav.terabox.com
# Username: seu_email@exemplo.com
# Password: sua_senha

# Montar
mkdir -p ~/terabox ~/gdrive
rclone mount terabox: ~/terabox --daemon
rclone mount gdrive: ~/gdrive --daemon

# Testar
ls ~/terabox
ls ~/gdrive
```

---

## 📊 Comparação: Online vs Local

| Feature | Online (Base44) | Local (HTML) |
|---------|-----------------|--------------|
| **Acesso** | URL pública | Arquivo local |
| **Instalação** | Zero | Zero |
| **Dependências** | Internet | Serviços locais |
| **Custo** | $0/mês | $0/mês |
| **Privacidade** | Depende do host | 100% local |
| **Offline** | ❌ | ✅ |
| **Portabilidade** | ❌ | ✅ USB/pendrive |
| **Atualizações** | Automático | Manual |

---

## 🎯 Casos de Uso

### 1. Desenvolvimento Web3
```javascript
// Deploy smart contract local
// Mint NFTs de teste
// Testar DApps sem gas
```

### 2. RAG (Retrieval Augmented Generation)
```javascript
// Indexar documentos no Qdrant
// Buscar semanticamente
// Gerar respostas com LLM local
```

### 3. ChromeOS com RAM Limitada
```bash
# Usar TeraBox como swap (2GB)
# Storage infinito (1TB)
# Zero impacto local
```

### 4. USB Bootável
```bash
# Copiar matverse-os.html para USB
# Rodar em qualquer máquina
# Sem instalação
```

---

## 🔧 Desenvolvimento

### Estrutura do Código
```javascript
// matverse-os.html (single-file)
<!DOCTYPE html>
<html>
  <head>
    <style>/* 500 linhas CSS */</style>
  </head>
  <body>
    <!-- 6 apps -->
    <script>/* 300 linhas JS */</script>
  </body>
</html>
```

### Adicionar Nova App
```javascript
// 1. Adicionar nav item
<div class="nav-item" onclick="switchApp('myapp')">
  <span class="nav-icon">🎨</span>
  <span>My App</span>
</div>

// 2. Adicionar view
<div class="app-view" id="myapp">
  <h1>My New App</h1>
  <!-- Seu conteúdo -->
</div>

// 3. Adicionar lógica
function myAppLogic() {
  // Sua funcionalidade
}
```

### Customizar Tema
```css
:root {
  --bg-primary: #0a0e1a;      /* Background escuro */
  --accent: #6366f1;          /* Cor primária */
  --text-primary: #e0e6ff;    /* Texto */
  /* ... */
}
```

---

## 🐛 Troubleshooting

### Problema: LLM não conecta
```bash
# Verificar se Ollama está rodando
pgrep -f "ollama serve"

# Testar endpoint
curl http://localhost:11434/api/version

# Reiniciar se necessário
pkill ollama
ollama serve &
```

### Problema: Vector search vazio
```bash
# Verificar Qdrant
curl http://localhost:6333/health

# Ver collections
curl http://localhost:6333/collections

# Criar collection se necessário
curl -X PUT http://localhost:6333/collections/dual_brain \
  -H 'Content-Type: application/json' \
  -d '{"vectors":{"size":1536,"distance":"Cosine"}}'
```

### Problema: Blockchain não responde
```bash
# Verificar Anvil
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Reiniciar se necessário
pkill anvil
anvil --gas-price 0 &
```

---

## 📈 Roadmap

### v1.0.0 (Atual) ✅
- [x] 6 apps básicas
- [x] Single-file HTML
- [x] ChromeOS support
- [x] Zero-cost pack

### v1.1.0 (Próximo)
- [ ] PWA completa
- [ ] Wallet UI (MetaMask)
- [ ] NFT gallery
- [ ] Code editor integrado

### v2.0.0 (Futuro)
- [ ] P2P file sharing
- [ ] Multi-chain support
- [ ] Mobile app (React Native)
- [ ] Desktop app (Electron)

---

## 🤝 Contribuir

### Como Contribuir
```bash
# 1. Fork o repositório
# 2. Crie branch
git checkout -b feature/minha-feature

# 3. Faça mudanças
# (edite matverse-os.html)

# 4. Commit
git commit -m "feat: Adiciona minha feature"

# 5. Push
git push origin feature/minha-feature

# 6. Abra PR
```

### Guidelines
- Manter single-file approach
- Sem dependências externas
- Tema dark-first
- Comentar código complexo
- Testar em Chrome, Firefox, Safari

---

## 📄 Licença

MIT License - Use livremente!

---

## 📞 Suporte

- 📖 **Docs**: README-CHROMEOS.md, INDEX.md
- 🐛 **Bugs**: GitHub Issues
- 💬 **Chat**: GitHub Discussions
- 🌐 **Site**: https://mat-verse-os-7363c48f.base44.app

---

## 🏆 Créditos

**MatVerse Team**
- Sistema Zero-Cost
- ChromeOS Optimization
- Dual-Brain Architecture
- LUA-AutoHeal Security

**Made with 🍒 in 2024**
