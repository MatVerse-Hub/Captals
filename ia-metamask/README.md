# 🤖 IA-MetaMask - Autonomous MetaMask AI

**Transform your MetaMask into an autonomous AI that auto-signs commits, mints NFTs, and deploys to Web3 — all without clicking.**

IA-MetaMask turns your MetaMask wallet into a code AI that:
✅ Auto-signs Git commits on-chain (proof of authorship)
✅ Mints NFTs of entire repositories (SHA-256 hash → Polygon)
✅ Publishes papers with DOI + NFT (Zenodo + OpenSea)
✅ Deploys HuggingFace models + proof NFTs
✅ **Costs**: ~0.0002 MATIC per signature (~$0.0001 USD)
✅ **Security**: Private key never leaves your machine
✅ **Time**: <3 minutes to setup

---

## 🚀 Quick Start (Copy & Paste)

### 1. Install (30 seconds)

```bash
# Clone repository
git clone https://github.com/MatVerse-Hub/test.git
cd test/ia-metamask

# Install dependencies
npm install

# Configure
cp .env.example .env
nano .env  # Add your PRIVATE_KEY (without 0x)
```

### 2. Start IA-MetaMask (2 methods)

**Method A: WalletConnect Mode** (recommended for mobile)
```bash
node ia-metamask.js
```
- Scan QR code with MetaMask mobile
- Approve connection
- All signature requests are now auto-approved! ✨

**Method B: API Server Mode** (recommended for automation)
```bash
node api-server.js
```
- HTTP API available at `http://localhost:3001`
- Use curl/scripts to sign messages and send transactions
- Perfect for CI/CD pipelines

### 3. Use It!

```bash
# Sign a message
curl -X POST http://localhost:3001/sign \
  -H "Content-Type: application/json" \
  -d '{"message":"commit 8f3a2b1c"}'

# Send transaction
curl -X POST http://localhost:3001/tx \
  -H "Content-Type: application/json" \
  -d '{"to":"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "value":"1000000000000000"}'

# Check status
curl http://localhost:3001/status
```

---

## 📚 What Can You Do?

### Auto-Sign Git Commits On-Chain

```bash
# Sign latest commit
COMMIT_HASH=$(git rev-parse HEAD)
curl -X POST http://localhost:3001/sign \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"commit $COMMIT_HASH\"}"

# Result: Proof of authorship stored on Polygon
```

### Mint NFT of Entire Repository

```bash
# Calculate repo hash
REPO_HASH=$(find . -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)

# Mint NFT
curl -X POST http://localhost:3001/tx \
  -H "Content-Type: application/json" \
  -d "{\"to\":\"0xNFT_CONTRACT\",\"data\":\"0x...mint($REPO_HASH)\"}"

# Result: NFT on OpenSea proving repo ownership
```

### Deploy Paper with DOI + NFT

```bash
# Use meta-dev wrapper (see below)
meta-dev paper my-paper.pdf

# Results:
#   1. Paper uploaded to arXiv
#   2. DOI generated via Zenodo
#   3. NFT minted with paper hash
#   4. Tweet posted with links
```

### Deploy HuggingFace Model + Proof NFT

```bash
meta-dev repo my-ai-model

# Results:
#   1. Pushed to GitHub
#   2. HuggingFace Space created
#   3. NFT minted as proof
#   4. Tweet with links
```

---

## 🛠️ Complete Workflow with `meta-dev`

IA-MetaMask integrates with **MatVerse-Copilot** via the `meta-dev` CLI:

```bash
# Copy meta-dev to your PATH
sudo cp ../meta-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/meta-dev

# Start IA-MetaMask API
meta-dev init

# Deploy repository
meta-dev repo symbios          # GitHub + HuggingFace + NFT

# Deploy paper
meta-dev paper QFCT.pdf        # arXiv + DOI + NFT

# Mint NFT
meta-dev nft evidence-001.png  # Polygon + OpenSea

# Check status
meta-dev status
```

**Result**: One command = GitHub + Web3 + HuggingFace + arXiv + Twitter — all automated.

---

## 🏗️ Architecture

### WalletConnect Mode (`ia-metamask.js`)

```
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│   Mobile    │  QR    │ IA-MetaMask  │  RPC   │   Polygon   │
│  MetaMask   │◄──────►│ WalletConnect│◄──────►│   Amoy      │
│             │ Approve│   Server     │  Sign  │             │
└─────────────┘        └──────────────┘        └─────────────┘
                              │
                              ▼
                       Auto-approves all
                       signature requests
```

**Workflow:**
1. Start `ia-metamask.js` → displays QR code
2. Scan with MetaMask mobile → approve connection
3. All future signature requests are auto-approved
4. Your MetaMask is now an autonomous AI! 🚀

### API Server Mode (`api-server.js`)

```
┌──────────┐   HTTP    ┌──────────────┐   RPC    ┌──────────┐
│   Your   │◄─────────►│   API Server │◄────────►│ Polygon  │
│  Scripts │  REST API │   Port 3001  │   ethers │   Amoy   │
└──────────┘           └──────────────┘          └──────────┘
                              │
                              ▼
                       Direct signing with
                       private key (local)
```

**Workflow:**
1. Start `api-server.js` → HTTP server on port 3001
2. Send POST requests to `/sign`, `/tx`, etc.
3. Server signs and broadcasts transactions
4. Perfect for automation & CI/CD

---

## 🔐 Security Best Practices

⚠️ **CRITICAL**: Your private key has full control of your wallet!

### DO ✅
- Use a **dedicated testnet wallet** (Polygon Amoy)
- Keep only small amounts of MATIC for gas fees
- Store `.env` file securely (never commit to Git)
- Use `.gitignore` to exclude `.env` file
- Run on a secure server (not public cloud)
- Monitor wallet activity regularly

### DON'T ❌
- **NEVER** use your main wallet
- **NEVER** commit `.env` to version control
- **NEVER** share your private key
- **NEVER** run on untrusted machines
- **NEVER** expose API server to the internet without authentication

### Recommended Setup

```bash
# 1. Create dedicated testnet wallet
# 2. Export private key from MetaMask
# 3. Get testnet MATIC from faucet
# 4. Configure IA-MetaMask with testnet key
# 5. Monitor with alerts (e.g., low balance warnings)
```

---

## 📋 API Reference

### Endpoints

#### `GET /status`
Get server status and statistics.

**Response:**
```json
{
  "status": "online",
  "network": "https://rpc-amoy.polygon.technology",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "balance": "1.234567890123456789 MATIC",
  "uptime": "2h 15m",
  "stats": {
    "requests": 42,
    "signatures": 15,
    "transactions": 8,
    "errors": 0
  }
}
```

#### `GET /address`
Get wallet address.

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

#### `GET /balance`
Get wallet balance.

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "balance": "1.234567890123456789",
  "unit": "MATIC"
}
```

#### `POST /sign`
Sign a message.

**Request:**
```json
{
  "message": "Hello MatVerse!"
}
```

**Response:**
```json
{
  "message": "Hello MatVerse!",
  "signature": "0x1234567890abcdef...",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

#### `POST /tx`
Send a transaction.

**Request:**
```json
{
  "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "value": "1000000000000000",
  "data": "0x"
}
```

**Response:**
```json
{
  "hash": "0xabcdef1234567890...",
  "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "value": "1000000000000000",
  "explorer": "https://amoy.polygonscan.com/tx/0xabcdef..."
}
```

#### `POST /signTx`
Sign a transaction (without sending).

**Request:**
```json
{
  "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "value": "1000000000000000",
  "data": "0x"
}
```

**Response:**
```json
{
  "signedTransaction": "0x...",
  "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

#### `POST /signTypedData`
Sign EIP-712 typed data.

**Request:**
```json
{
  "domain": {
    "name": "MyDApp",
    "version": "1",
    "chainId": 80002
  },
  "types": {
    "Message": [
      { "name": "content", "type": "string" }
    ]
  },
  "message": {
    "content": "Hello!"
  }
}
```

**Response:**
```json
{
  "signature": "0x1234567890abcdef...",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

---

## 🧪 Testing

### Test Signature

```bash
curl -X POST http://localhost:3001/sign \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### Test Transaction

```bash
# Send 0.001 MATIC to yourself
curl -X POST http://localhost:3001/tx \
  -H "Content-Type: application/json" \
  -d '{"to":"YOUR_ADDRESS","value":"1000000000000000"}'
```

### Test Status

```bash
curl http://localhost:3001/status | jq
```

---

## 🌐 Integration Examples

### Integrate with Git Hooks

Sign every commit automatically:

```bash
# .git/hooks/post-commit
#!/bin/bash
COMMIT_HASH=$(git rev-parse HEAD)
curl -X POST http://localhost:3001/sign \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"commit $COMMIT_HASH\"}" \
  -s > .commit-signature.json
```

### Integrate with CI/CD

GitHub Actions workflow:

```yaml
name: Sign & Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sign commit
        run: |
          curl -X POST ${{ secrets.IA_METAMASK_URL }}/sign \
            -H "Content-Type: application/json" \
            -d "{\"message\":\"commit $GITHUB_SHA\"}"
```

### Integrate with MatVerse-Copilot

Automated deployment pipeline:

```bash
# 1. Start IA-MetaMask API
meta-dev init

# 2. Start MatVerse-Copilot
matverse-copilot start -d

# 3. Deploy everything
meta-dev repo my-project    # Auto-signs + deploys + mints NFT
```

---

## 📦 Dependencies

- **Node.js** ≥ 18.0.0
- **ethers** ^6.13.0 - Ethereum library
- **@walletconnect/web3wallet** ^1.12.0 - WalletConnect v2
- **express** ^4.19.2 - HTTP server
- **dotenv** ^16.4.5 - Environment variables
- **qrcode-terminal** ^0.12.0 - QR code display
- **axios** ^1.7.2 - HTTP client

---

## 🎯 Use Cases

### 1. **Provable Code Authorship**
Sign Git commits on-chain → immutable proof you wrote the code.

### 2. **Repository NFTs**
Mint NFTs representing entire codebases → prove ownership & track versions.

### 3. **Paper Publishing**
Deploy papers to arXiv + Zenodo DOI + mint NFT → full academic provenance.

### 4. **AI Model Deployment**
Deploy to HuggingFace + mint proof NFT → track model lineage.

### 5. **Automated CI/CD**
Integrate with GitHub Actions → auto-sign releases, mint version NFTs.

### 6. **DAO Governance**
Auto-sign governance proposals → transparent on-chain voting.

---

## 🐛 Troubleshooting

### Error: "PRIVATE_KEY not found"
```bash
# Solution: Create .env file
cp .env.example .env
nano .env  # Add PRIVATE_KEY=your_key_without_0x
```

### Error: "insufficient funds"
```bash
# Solution: Get testnet MATIC
# Visit: https://faucet.polygon.technology/
# Select "Polygon Amoy Testnet"
# Paste your address
```

### Error: "Failed to initialize WalletConnect"
```bash
# Solution 1: Check internet connection
ping cloud.walletconnect.com

# Solution 2: Get free Project ID
# Visit: https://cloud.walletconnect.com
# Create account → Get Project ID
# Add to .env: WALLETCONNECT_PROJECT_ID=your_id
```

### API Server won't start
```bash
# Check if port 3001 is already in use
lsof -i :3001

# Use different port
API_PORT=3002 node api-server.js
```

### WalletConnect QR code not scanning
```bash
# Solution 1: Make QR code larger
# Edit ia-metamask.js: qrcode.generate(uri, { small: false })

# Solution 2: Copy URI manually
# The URI is printed below the QR code
# Paste in MetaMask → WalletConnect
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](../matverse-copilot/LICENSE) file

---

## 🔗 Links

- **GitHub**: https://github.com/MatVerse-Hub/test
- **MatVerse-Copilot**: [../matverse-copilot](../matverse-copilot)
- **Polygon Amoy**: https://amoy.polygonscan.com
- **OpenSea Testnet**: https://testnets.opensea.io
- **WalletConnect**: https://cloud.walletconnect.com

---

## 💡 Next Steps

1. **Start the AI**: `node ia-metamask.js`
2. **Scan QR code** with MetaMask mobile
3. **Test signing**: `curl -X POST http://localhost:3001/sign -d '{"message":"test"}'`
4. **Deploy something**: `meta-dev repo my-project`

**Your MetaMask is now an autonomous AI! 🚀**

Never click "Sign" again. Let the AI handle it.

---

**Made with ❤️ by MatVerse Hub**
