# MatVerse Hub - Web3 AI Development Platform

**Transform MetaMask into an autonomous AI for code, NFTs, and academic publishing**

This repository contains two powerful tools that work together to create a complete Web3 + AI development workflow:

## 🤖 IA-MetaMask - Autonomous MetaMask AI

**Turn your MetaMask into a code AI that never needs clicking again**

IA-MetaMask makes your wallet autonomous:
- ✅ Auto-signs Git commits on-chain (proof of authorship)
- ✅ Mints NFTs of repositories (SHA-256 → Polygon)
- ✅ Publishes papers with DOI + NFT (Zenodo + OpenSea)
- ✅ Deploys HuggingFace models + proof NFTs
- ✅ **Cost**: ~0.0002 MATIC per signature (~$0.0001 USD)
- ✅ **Setup**: <3 minutes

### Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/ia-metamask/install-quick.sh | bash
```

See [ia-metamask/README.md](./ia-metamask/README.md) for full documentation.

---

## 🚀 MatVerse-Copilot - Automated Deployment System

**Automated deployment and NFT minting system**

MatVerse-Copilot is an intelligent automation system that monitors a deployment queue, automatically mints NFTs on Polygon Amoy, posts to Twitter, and deploys to multiple platforms.

### Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/matverse-copilot/install-quick.sh | bash
```

### Features

- 🔍 24/7 Queue Monitoring - Watches `~/deploy-queue/` for new files
- 🎨 Automatic NFT Minting - Mints evidence notes on Polygon Amoy
- 🐦 Twitter Integration - Auto-posts tweets
- 📦 Multi-Platform Deploy - GitHub, HuggingFace, Vercel, arXiv, OpenSea
- ⏰ Scheduled Deployments - Schedule tasks with filename-based timing
- 🛠️ CLI Interface - Full command-line control

### Documentation

See [matverse-copilot/README.md](./matverse-copilot/README.md) for full documentation.

### Usage

```bash
# Start monitoring
matverse-copilot start -d

# Mint NFT
cp image.png ~/deploy-queue/now_evidence-001_nft.png

# Post tweet
echo "Hello MatVerse! 🚀" > ~/deploy-queue/now_tweet.txt

# Check status
matverse-copilot status
```

---

## 🛠️ Complete Workflow with `meta-dev`

The `meta-dev` CLI unifies both tools into a single command:

```bash
# 1. Start IA-MetaMask API
meta-dev init

# 2. Deploy repository (GitHub + HuggingFace + NFT)
meta-dev repo symbios

# 3. Deploy paper (arXiv + DOI + NFT)
meta-dev paper QFCT.pdf

# 4. Mint NFT (Polygon + OpenSea)
meta-dev nft evidence-001.png

# 5. Check status
meta-dev status
```

**Result**: One command = GitHub + Web3 + HuggingFace + arXiv + Twitter — fully automated! 🚀

---

## 📚 Documentation

- **IA-MetaMask**: [ia-metamask/README.md](./ia-metamask/README.md)
- **MatVerse-Copilot**: [matverse-copilot/README.md](./matverse-copilot/README.md)
- **meta-dev CLI**: [meta-dev](./meta-dev) (unified interface)

---

## 🎯 Use Cases

### Academic Publishing
- Deploy papers to arXiv
- Generate DOIs via Zenodo
- Mint NFTs as proof of authorship
- Auto-post to Twitter

### Code Provenance
- Sign commits on-chain
- Mint repository NFTs
- Track code lineage
- Prove ownership

### AI Model Deployment
- Deploy to HuggingFace
- Mint proof NFTs
- Track model versions
- Integrate with Web3

### Automated CI/CD
- GitHub Actions integration
- Auto-sign releases
- Mint version NFTs
- Web3-native deployment

---

**License**: MIT