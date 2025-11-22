# Omega Capitals (Ω-Capitals) - Advanced DeFi Ecosystem

**Omega Capitals** is a comprehensive DeFi platform integrating Ω-Score-based governance, tokenized financial products (Ω-Funds, Ω-Bonds, Ω-Futures), wallet integration, and automation via bots.

## 🏗️ Architecture

- **Blockchain**: Solidity contracts deployed on Polygon (Amoy/Mainnet) and Sepolia
- **Backend**: FastAPI with Web3.py, Redis, and PostgreSQL
- **Frontend**: React with Vite, Recharts for dashboards
- **Payment**: LUA-PAY integration for crypto-fiat transactions
- **Bot**: Telegram bot with AI-powered sales agent
- **Deployment**: Docker, Hugging Face Spaces, CI/CD via GitHub Actions

## 📊 Core Components

### Ω-Score System
The Omega Score is calculated using:
```
Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
```
Where:
- **Ψ (Psi)**: Asset quality metrics
- **Θ (Theta)**: Risk-adjusted returns
- **CVaR**: Conditional Value at Risk
- **PoLE**: Proof of Liquidity Efficiency

### Products
1. **Ω-Funds**: Tokenized ETF-like investment funds
2. **Ω-Bonds**: Fixed-income tokenized bonds
3. **Ω-Futures**: Derivative contracts for hedging
4. **Evidence Notes**: Soulbound NFTs for certification and proof of investment

### LUA-PAY Integration
Seamless crypto-fiat payment gateway supporting:
- USDT, ETH, MATIC payments
- Fiat conversion with hedging
- MetaMask and mobile wallet support
- Invoice generation and webhook verification

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- MetaMask or compatible wallet

### Setup
```bash
# Clone repository
git clone <repository-url>
cd omega-capitals

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Quick deploy (local development)
chmod +x quick-deploy.sh
./quick-deploy.sh

# Deploy contracts to testnet
npx hardhat run scripts/deploy-testnet.js --network sepolia

# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start frontend
cd frontend
npm install
npm run dev

# Start Telegram bot
cd bot
pip install -r requirements.txt
python bot.py
```

## 📁 Project Structure

```
omega-capitals/
├── contracts/          # Solidity smart contracts
│   ├── core/          # Core system contracts
│   ├── products/      # Financial products
│   └── libraries/     # Shared libraries (OmegaScore)
├── scripts/           # Deployment scripts
├── backend/           # FastAPI backend
│   ├── routes/        # API routes
│   └── services/      # Business logic
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── pages/
├── bot/               # Telegram bot
├── docs/              # Documentation
├── huggingface/       # HF Spaces integration
└── .github/workflows/ # CI/CD
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Blockchain
ALCHEMY_API_KEY=your_alchemy_key
POLYGON_RPC=https://rpc.ankr.com/polygon_amoy
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=your_wallet_private_key

# LUA-PAY
LUA_PAY_API_KEY=your_lua_pay_key
LUA_PAY_SECRET=your_lua_pay_secret
LUA_PAY_WEBHOOK_URL=https://your-backend.com/api/payments/webhook

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_token

# Database
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_URL=postgresql://postgres:secret@localhost/omega
```

## 📚 Documentation

- **Whitepaper**: [docs/whitepaper.md](docs/whitepaper.md)
- **Pitch Deck**: [docs/pitch-deck.md](docs/pitch-deck.md)
- **LUA-PAY Integration**: See backend/services/lua_pay_service.py

## 🧪 Testing

```bash
# Test contracts
npx hardhat test

# Test backend
cd backend
pytest

# Test frontend
cd frontend
npm test
```

## 🚢 Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Testnet Deployment
```bash
npx hardhat run scripts/deploy-testnet.js --network amoy
npx hardhat run scripts/deploy-testnet.js --network sepolia
```

### Production Deployment
```bash
npx hardhat run scripts/deploy-mainnet.js --network polygon
```

## 🤝 Contributing

Contributions are welcome! Please follow the standard fork-and-pull request workflow.

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- **Website**: Coming soon
- **Dashboard**: Deployed on Hugging Face Spaces
- **Telegram Bot**: @OmegaCapitalsBot

---

**Built with ❤️ for the future of DeFi**
