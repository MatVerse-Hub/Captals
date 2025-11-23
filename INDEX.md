# 🍒 MatVerse Zero-Cost Pack - Índice de Navegação

## 📋 Guia Rápido de Navegação

Bem-vindo ao MatVerse Zero-Cost Pack! Use este índice para encontrar rapidamente o que você precisa.

---

## 🚀 Começar Agora

| Documento | Descrição | Para Quem |
|-----------|-----------|-----------|
| **[README-CHROMEOS.md](./README-CHROMEOS.md)** | Guia completo para Chromebooks | Usuários de ChromeOS ✅ |
| **[README.md](./README.md)** | Guia completo para Linux | Usuários de Linux/Ubuntu |
| **[QUICK_START.md](#)** | Setup em 5 minutos | Todos os usuários |

---

## 📦 Instaladores

### ChromeOS
```bash
curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero-chromeos.sh | bash
```
📄 **[Código fonte](./installers/zero-chromeos.sh)**

### Linux
```bash
curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero.sh | bash
```
📄 **[Código fonte](./installers/zero.sh)**

---

## 🧠 Componentes Principais

### 1. SessionStart Hook
- **Arquivo**: [.claude/session-start-hook.yaml](./.claude/session-start-hook.yaml)
- **Função**: Auto-bootstrap quando abre Claude Code web
- **Uso**: Automático (configurado via Claude Code settings)

### 2. Dual-Brain Watcher
- **Arquivo**: [watcher/dual_brain_sync.py](./watcher/dual_brain_sync.py)
- **Função**: Monitora TeraBox + GDrive → Indexa em Qdrant
- **Uso**: `python3 watcher/dual_brain_sync.py`

### 3. CLI MatVerse
- **Instalado em**: `~/.local/bin/matverse`
- **Comandos**:
  - `matverse status` - Health check
  - `matverse deploy` - Sobe interface web
  - `matverse swap-on` - Ativa swap (ChromeOS)
  - `matverse swap-off` - Desativa swap (ChromeOS)

---

## 📚 Documentação por Tópico

### Instalação
- [README-CHROMEOS.md](./README-CHROMEOS.md) - ChromeOS completo
- [README.md](./README.md) - Linux completo

### Arquitetura
- [XI-LUA-v2-SUMMARY.md](./XI-LUA-v2-SUMMARY.md) - LUA-AutoHeal
- Dual-Brain: Ver README-CHROMEOS.md seção "Dual-Brain"

### Segurança
- LUA-AutoHeal: 8 camadas de segurança
- Swap encryption: Ver troubleshooting
- TeraBox security: Ver README-CHROMEOS.md seção "Segurança"

### Troubleshooting
- ChromeOS: [README-CHROMEOS.md](./README-CHROMEOS.md#-troubleshooting)
- Linux: [README.md](./README.md#troubleshooting)

---

## 🗂️ Estrutura de Diretórios

```
MatVerse-Hub/test/
├── 📖 Documentação
│   ├── INDEX.md (este arquivo)
│   ├── README.md (Linux)
│   ├── README-CHROMEOS.md (ChromeOS) ⭐
│   └── XI-LUA-v2-SUMMARY.md (LUA-AutoHeal)
│
├── 🔧 Componentes
│   ├── .claude/
│   │   └── session-start-hook.yaml (Auto-bootstrap)
│   │
│   ├── installers/
│   │   ├── zero.sh (Linux installer)
│   │   └── zero-chromeos.sh (ChromeOS installer) ⭐
│   │
│   ├── watcher/
│   │   ├── dual_brain_sync.py (Monitor)
│   │   └── requirements.txt (Deps)
│   │
│   ├── xi-lua/ (LUA-AutoHeal)
│   │   ├── ξ-lua (CLI)
│   │   └── core/autoheal/
│   │
│   ├── contracts/ (Smart Contracts)
│   │   └── omega-capitals/
│   │
│   ├── ia-metamask/ (Wallet Autônoma)
│   └── scripts/ (Utilitários)
│
└── 📦 Meta
    ├── docker-compose.yml (Infra)
    ├── package.json (Node deps)
    └── .env.example (Config template)
```

---

## 🎯 Casos de Uso

### Para Chromebook (RAM/Storage limitados)
👉 **[README-CHROMEOS.md](./README-CHROMEOS.md)**
- Swap virtual 2GB
- Storage infinito (TeraBox)
- Custo $0/mês

### Para Servidor Linux
👉 **[README.md](./README.md)**
- Qdrant em Docker
- Anvil blockchain local
- Múltiplos LLMs

### Para Desenvolvimento Web3
👉 **[contracts/](./contracts/)**
- Omega Capitals DeFi
- PoLE/PoSE proofs
- Ω-GATE governance

### Para IA/RAG
👉 **[watcher/dual_brain_sync.py](./watcher/dual_brain_sync.py)**
- Indexação automática
- Embeddings únicos
- Query unificada

---

## 🔗 Links Rápidos

### GitHub
- [Repositório](https://github.com/MatVerse-Hub/test)
- [Issues](https://github.com/MatVerse-Hub/test/issues)
- [Pull Requests](https://github.com/MatVerse-Hub/test/pulls)

### Externos
- [TeraBox](https://terabox.com) - 1TB grátis
- [Ollama](https://ollama.ai) - LLM local
- [Qdrant](https://qdrant.tech) - Vector database

---

## ❓ FAQ

### P: Qual instalador usar?
**R**: ChromeOS? Use `zero-chromeos.sh`. Linux? Use `zero.sh`.

### P: Preciso de API keys?
**R**: Não! Tudo roda local (zero-cost). APIs são opcionais.

### P: Quanto de RAM preciso?
**R**: Mínimo 2GB. Recomendado 4GB. ChromeOS compensa com swap.

### P: Funciona offline?
**R**: Sim! Apenas mount do TeraBox precisa de internet.

### P: É seguro?
**R**: Sim! LUA-AutoHeal tem 8 camadas de segurança. Dados sensíveis ficam locais.

---

## 🏆 Roadmap

- [x] ChromeOS support ✅
- [x] Linux support ✅
- [x] SessionStart hook ✅
- [x] Dual-Brain watcher ✅
- [ ] macOS support
- [ ] Windows support
- [ ] ISO bootável (64MB)
- [ ] Mobile app (Android/iOS)

---

## 🤝 Contribuir

1. Fork o repositório
2. Crie branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'feat: Minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra PR

---

## 📞 Suporte

- 📖 **Leia primeiro**: [README-CHROMEOS.md](./README-CHROMEOS.md) (ChromeOS) ou [README.md](./README.md) (Linux)
- 🐛 **Bugs**: [GitHub Issues](https://github.com/MatVerse-Hub/test/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/MatVerse-Hub/test/discussions)

---

## 🎉 Começar Agora!

### ChromeOS (Recomendado para você)
```bash
curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero-chromeos.sh | bash
```

### Linux
```bash
curl -sSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/installers/zero.sh | bash
```

---

**Made with ❤️ by MatVerse Team**

🍒 *Zero-Cost. Maximum Impact.*
