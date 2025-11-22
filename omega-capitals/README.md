# 🎯 Ω OMEGA CAPITALS

**Portfolio Risk Management & Evidence System on Blockchain**

Complete monorepo for Omega Capitals - a decentralized portfolio risk assessment platform using the **Ω-Score** metric, deployed on Polygon.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Smart Contracts](#smart-contracts)
- [Formula](#formula)

---

## 🌟 Overview

Omega Capitals is a comprehensive DeFi risk management system that evaluates portfolio strategies using a proprietary **Ω-Score** metric combining:

- **CVaR (Conditional Value at Risk):** 95% tail risk measure
- **β (Beta Coefficient):** Market correlation
- **ERR₅m (5-minute Error):** Maximum short-term deviation
- **Idem (Idempotency):** Strategy consistency

**Formula:**
```
Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
```

**Risk Tiers:**
- 🟢 **Low Risk:** Ω ≥ 800
- 🟡 **Medium Risk:** 600 ≤ Ω < 800
- 🟠 **High Risk:** 400 ≤ Ω < 600
- 🔴 **Critical Risk:** Ω < 400

---

## ✨ Features

### Smart Contracts (Solidity)
- ✅ **EvidenceNotes:** ERC-721 NFTs for immutable strategy evidence
- ✅ **OmegaPool:** Liquidity pool with Ω-Score gating (min 600)
- ✅ **TreasuryVault:** Multi-sig treasury for protocol fees
- ✅ **OmegaGovernance:** Voting system weighted by Ω-Score

### Backend (FastAPI)
- ✅ Ω-Score computation API
- ✅ Web3 integration (Polygon)
- ✅ NFT minting endpoints
- ✅ Pool statistics & strategy management

### Frontend (React + Vite)
- ✅ Real-time dashboard with Recharts
- ✅ Radar charts for risk visualization
- ✅ Pool TVL tracking
- ✅ Dark theme with terminal aesthetics

### Telegram Bot
- ✅ `/omega` - Compute Ω-Score
- ✅ `/mint` - Mint Evidence NFT
- ✅ `/pool` - Pool statistics
- ✅ Interactive menus

### Hugging Face Spaces
- ✅ Gradio web interface
- ✅ No-code Ω-Score calculator
- ✅ NFT minting UI
- ✅ Public deployment ready

---

## 🏗️ Architecture

```
omega-capitals/
├── contracts/                # Solidity smart contracts
│   ├── core/
│   │   └── EvidenceNotes.sol
│   ├── libraries/
│   │   └── OmegaScore.sol
│   ├── products/
│   │   ├── OmegaPool.sol
│   │   ├── TreasuryVault.sol
│   │   └── OmegaGovernance.sol
│   ├── hardhat.config.js
│   └── package.json
│
├── backend/                  # FastAPI Python backend
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── abis/                # Contract ABIs
│
├── frontend/                 # React + Vite dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── bot/                      # Telegram bot
│   ├── bot.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── huggingface/              # Gradio Space
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── scripts/                  # Deploy scripts
│   ├── deploy-testnet.js
│   └── deploy-mainnet.js
│
├── docker-compose.yml        # Full stack orchestration
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.11
- Docker & Docker Compose
- Polygon wallet with testnet MATIC

### 1. Clone Repository

```bash
git clone https://github.com/your-username/omega-capitals.git
cd omega-capitals
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

**Required Variables:**
```env
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
PUBLIC_KEY=0x...
PRIVATE_KEY=...
TELEGRAM_BOT_TOKEN=...
```

### 3. Deploy Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat run ../scripts/deploy-testnet.js --network amoy
```

**Save contract addresses** to `.env` and `backend/abis/deployment-amoy.json`

### 4. Start Full Stack

```bash
cd ..
docker compose up --build -d
```

### 5. Access Services

- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Hugging Face UI:** http://localhost:7860
- **API Docs:** http://localhost:8000/docs
- **Telegram Bot:** @your_omega_bot

---

## 🌐 Deployment

### Testnet (Polygon Amoy)

```bash
# 1. Deploy contracts
cd contracts
npm run deploy:testnet

# 2. Start services
cd ..
docker compose up -d
```

### Mainnet (Polygon)

**⚠️ WARNING: Real funds!**

```bash
# 1. Set confirmation flag
export CONFIRM_MAINNET_DEPLOY=true

# 2. Deploy contracts
cd contracts
npm run deploy:mainnet

# 3. Verify on PolygonScan
npx hardhat verify --network polygon <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>

# 4. Update .env with mainnet addresses
# 5. Restart services
docker compose restart
```

### Hugging Face Spaces

```bash
# 1. Create Space on https://huggingface.co/spaces
# 2. Clone Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/omega-capitals

# 3. Copy files
cp -r huggingface/* omega-capitals-space/

# 4. Set API_URL secret in Space settings
# 5. Push
cd omega-capitals-space
git add .
git commit -m "Deploy Omega Capitals"
git push
```

---

## 📡 API Documentation

### Compute Ω-Score

```bash
POST /api/omega/compute
Content-Type: application/json

{
  "cvar": 0.15,
  "beta": 0.6,
  "err5m": 0.05,
  "idem": 0.95
}
```

**Response:**
```json
{
  "omega_score": 823,
  "risk_tier": "Low Risk",
  "metrics": {
    "cvar": 0.15,
    "beta": 0.6,
    "err5m": 0.05,
    "idem": 0.95
  },
  "breakdown": {
    "cvar_contribution": 340.0,
    "beta_contribution": 120.0,
    "err5m_contribution": 190.0,
    "idem_contribution": 95.0
  }
}
```

### Mint Evidence NFT

```bash
POST /api/nft/mint
Content-Type: application/json

{
  "to": "0x742d35Cc6634C0532925a3b844Bc9e7bb337ab...",
  "uri": "ipfs://QmXyz..."
}
```

### Pool Statistics

```bash
GET /api/pool/tvl
```

**Full API docs:** http://localhost:8000/docs

---

## 📜 Smart Contracts

### EvidenceNotes.sol

ERC-721 NFT for immutable strategy evidence.

**Functions:**
- `mint(address to, string uri)` - Mint new evidence note
- `batchMint(address[] recipients, string[] uris)` - Batch mint
- `totalSupply()` - Total minted

### OmegaPool.sol

Liquidity pool with Ω-Score gating.

**Functions:**
- `addStrategy(address manager, uint256 cvar, beta, err5m, idem)` - Add strategy (requires Ω ≥ 600)
- `deposit(uint256 amount)` - Deposit USDC
- `withdraw(uint256 shares)` - Redeem shares
- `allocateCapital(uint256 strategyId, amount)` - Fund strategy
- `recordPerformance(uint256 strategyId, newValue)` - Update PnL

### TreasuryVault.sol

Multi-sig treasury for protocol funds.

**Functions:**
- `createProposal(address recipient, uint256 amount, address token, string description)` - Create withdrawal
- `approveProposal(uint256 proposalId)` - Approve (auto-executes at threshold)
- `addSigner(address signer)` - Add signer (owner)
- `setRequiredApprovals(uint256 newThreshold)` - Update threshold

### OmegaGovernance.sol

Voting system weighted by Ω-Score.

**Functions:**
- `registerVoter(uint256 cvar, beta, err5m, idem)` - Register with Ω-Score
- `propose(string title, description)` - Create proposal
- `castVote(uint256 proposalId, bool support)` - Vote (power = tokens × (1 + Ω/1000))
- `execute(uint256 proposalId)` - Execute passed proposal

---

## 📊 Formula

### Ω-Score Calculation

```
Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
```

**Weights:**
- **40%** - CVaR (tail risk)
- **30%** - Beta (market risk)
- **20%** - ERR₅m (execution risk)
- **10%** - Idempotency (consistency)

**Example:**
```
CVaR = 0.15, β = 0.6, ERR₅m = 0.05, Idem = 0.95

Ω = 0.4(1-0.15) + 0.3(1-0.6) + 0.2(1-0.05) + 0.1(0.95)
  = 0.4(0.85) + 0.3(0.4) + 0.2(0.95) + 0.1(0.95)
  = 0.34 + 0.12 + 0.19 + 0.095
  = 0.745

Scaled: 0.745 × 1000 = 745 (Medium Risk)
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Contract Tests

```bash
cd contracts
npx hardhat test
```

### Frontend Tests

```bash
cd frontend
npm run test
```

---

## 🛠️ Development

### Run Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

### Run Bot Locally

```bash
cd bot
pip install -r requirements.txt
python bot.py
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📞 Support

- **Documentation:** https://docs.omega-capitals.io
- **Discord:** https://discord.gg/omega-capitals
- **Twitter:** [@OmegaCapitals](https://twitter.com/OmegaCapitals)
- **Telegram:** @OmegaCapitalsBot

---

## 🎯 Roadmap

- [ ] Mainnet deployment
- [ ] Governance token launch
- [ ] Additional risk metrics (Sharpe, Sortino)
- [ ] AI-powered strategy analysis
- [ ] Mobile app (React Native)
- [ ] Multi-chain support (Arbitrum, Optimism)

---

**Built with ❤️ by the Omega Capitals Team**

*Powered by Solidity, FastAPI, React & Web3*
