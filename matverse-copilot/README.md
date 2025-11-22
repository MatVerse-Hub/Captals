# 🚀 MatVerse-Copilot

**Automated deployment and NFT minting system for MatVerse**

MatVerse-Copilot is an intelligent automation system that monitors a deployment queue, automatically mints NFTs on Polygon Amoy, posts to Twitter, and deploys to multiple platforms (GitHub, HuggingFace, Vercel, arXiv, OpenSea).

---

## ✨ Features

- 🔍 **24/7 Queue Monitoring** - Watches `~/deploy-queue/` for new files
- 🎨 **Automatic NFT Minting** - Mints evidence notes on Polygon Amoy testnet
- 🐦 **Twitter Integration** - Auto-posts tweets with Twitter API v2
- 📦 **Multi-Platform Deploy** - GitHub, HuggingFace, Vercel, arXiv, OpenSea
- ⏰ **Scheduled Deployments** - Schedule tasks with filename-based timing
- 🛠️ **CLI Interface** - Full command-line control
- 🔐 **MetaMask Compatible** - Web3 integration with Polygon

---

## 🚀 Quick Install

**One-line installation (8-10 minutes):**

```bash
curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/matverse-copilot/install-quick.sh | bash
```

Or manual installation:

```bash
# Clone repository
git clone https://github.com/MatVerse-Hub/test.git
cd test/matverse-copilot

# Install
pip3 install -e .

# Create queue directory
mkdir -p ~/deploy-queue

# Configure
cp .env.example .env
nano .env  # Add your credentials
```

---

## ⚙️ Configuration

Edit `.env` with your credentials:

```bash
# Polygon Amoy (Testnet)
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
WALLET_PRIVATE_KEY=your_private_key_here
NFT_CONTRACT_ADDRESS=0x...

# Twitter API v2
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

# GitHub
GITHUB_TOKEN=...

# HuggingFace
HUGGINGFACE_TOKEN=...
```

### 🔑 Getting Your Credentials

1. **Polygon Wallet**: Export private key from MetaMask
2. **Twitter API**: Apply at https://developer.twitter.com/
3. **GitHub Token**: Settings → Developer Settings → Personal Access Tokens
4. **HuggingFace**: Settings → Access Tokens

---

## 📋 Usage

### Start the Monitor

```bash
# Run in foreground
matverse-copilot start

# Run in background (daemon)
matverse-copilot start -d
```

### Check Status

```bash
matverse-copilot status
```

Output:
```
==================================================
MatVerse-Copilot Status
==================================================

● Status: RUNNING
  PID: 12345
  CPU: 0.5%
  Memory: 45.2 MB
  Uptime: 2h 15m

Queue Information:
  Path: /home/user/deploy-queue
  Exists: ✓
  Pending files: 3
```

### View Logs

```bash
# Show last 50 lines
matverse-copilot logs

# Follow logs in real-time
matverse-copilot logs -f
```

### View Queue

```bash
matverse-copilot queue
```

### Stop/Restart

```bash
matverse-copilot stop
matverse-copilot restart
```

---

## 🎯 How It Works

### File Naming Conventions

Drop files into `~/deploy-queue/` with specific naming patterns:

#### 1. **Immediate Execution** (prefix: `now_`)

```bash
# Mint NFT immediately
cp image.png ~/deploy-queue/now_evidence-001_nft.png

# Post tweet immediately
echo "MatVerse is live! 🚀" > ~/deploy-queue/now_tweet.txt

# Deploy paper
cp paper.pdf ~/deploy-queue/now_QFCT-paper.pdf
```

#### 2. **Scheduled Execution** (format: `YYYY-MM-DD_HHhMM_`)

```bash
# Schedule for tomorrow at 21:00
cp -r project/ ~/deploy-queue/2025-11-23_21h00_SymbiOS-v2/

# Schedule tweet for next week
echo "New release!" > ~/deploy-queue/2025-11-29_10h30_tweet.txt
```

### Supported File Types

| Extension | Action |
|-----------|--------|
| `.png`, `.jpg`, `.jpeg` | Mint as NFT (if `_nft` in filename) |
| `.txt` | Post as tweet (if `_tweet` in filename) |
| `.pdf` | Deploy to arXiv/GitHub |
| Directory | Deploy to platform based on content |

---

## 🧪 Testing

### Test NFT Minting

```bash
# Create test image
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > /tmp/test.png

# Mint NFT
cp /tmp/test.png ~/deploy-queue/now_evidence-000_nft.png

# Wait 60 seconds, then check OpenSea
# https://testnets.opensea.io/account
```

### Test Twitter Bot

```bash
# Post test tweet
echo "MatVerse-Copilot test $(date)" > ~/deploy-queue/now_tweet.txt

# Check your Twitter timeline
```

### Run System Tests

```bash
# Test all systems
matverse-copilot test all

# Test NFT only
matverse-copilot test nft

# Test Twitter only
matverse-copilot test twitter
```

---

## 📦 Examples

### Mint 10 Evidence Notes

```bash
for i in {1..10}; do
  cp note-$i.png ~/deploy-queue/now_evidence-$(printf "%03d" $i)_nft.png
done
```

### Deploy Paper with DOI

```bash
cp QFCT-528φ.pdf ~/deploy-queue/now_QFCT-paper.pdf
```

### Schedule Multiple Releases

```bash
# Monday 9 AM - Release v1
cp -r release-v1/ ~/deploy-queue/2025-11-24_09h00_release-v1/

# Wednesday 2 PM - Release v2
cp -r release-v2/ ~/deploy-queue/2025-11-26_14h00_release-v2/

# Friday 5 PM - Release v3
cp -r release-v3/ ~/deploy-queue/2025-11-28_17h00_release-v3/
```

---

## 🏗️ Architecture

```
matverse-copilot/
├── src/
│   ├── __init__.py
│   ├── monitor.py       # Main queue monitor (watchdog)
│   ├── nft_minter.py    # Web3 NFT minting
│   ├── twitter_bot.py   # Twitter API v2 integration
│   ├── deployer.py      # Multi-platform deployment
│   └── cli.py           # Command-line interface
├── contracts/
│   ├── EvidenceNFT.sol  # Solidity smart contract
│   └── EvidenceNFT.json # Contract ABI
├── scripts/             # Utility scripts
├── tests/               # Unit tests
├── install-quick.sh     # One-line installer
├── setup.py             # Python package setup
├── requirements.txt     # Dependencies
├── .env.example         # Configuration template
└── README.md
```

---

## 🔧 Development

### Install in Development Mode

```bash
git clone https://github.com/MatVerse-Hub/test.git
cd test/matverse-copilot
pip3 install -e .[dev]
```

### Run Tests

```bash
pytest tests/
```

### Deploy Smart Contract

The ERC721 contract is in `contracts/EvidenceNFT.sol`. Deploy using Remix or Hardhat:

```bash
# Using Hardhat
npx hardhat run scripts/deploy.js --network polygonAmoy
```

Update `.env` with the deployed contract address.

---

## 🌐 Links

- **OpenSea Testnet**: https://testnets.opensea.io
- **Polygon Amoy Explorer**: https://amoy.polygonscan.com
- **Twitter Developer**: https://developer.twitter.com
- **MatVerse GitHub**: https://github.com/MatVerse-Hub

---

## 📝 License

MIT License - see LICENSE file

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

---

## 📞 Support

- GitHub Issues: https://github.com/MatVerse-Hub/test/issues
- Twitter: [@MatVerse_Hub](https://twitter.com/MatVerse_Hub)

---

## 🎉 Ready to Go!

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/matverse-copilot/install-quick.sh | bash

# Configure
nano ~/matverse-copilot/.env

# Start
matverse-copilot start -d

# Test
echo "Hello MatVerse! 🚀" > ~/deploy-queue/now_tweet.txt
```

**Happy deploying! 🚀**
