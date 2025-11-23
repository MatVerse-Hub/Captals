# CLAUDE.md - AI Assistant Guide for Omega Capitals DeFi Ecosystem

> **Purpose**: This document provides AI assistants with comprehensive context about the Omega Capitals codebase structure, development workflows, and key conventions to follow when making changes.

**Last Updated**: 2025-11-23
**Repository**: MatVerse-Hub/test
**Primary Branch**: main
**Current Development Branch**: claude/claude-md-miazrgai9yyoznsh-01VYBahhS6Z7KWGmjnksjvgw

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Technology Stack](#technology-stack)
4. [Development Workflows](#development-workflows)
5. [Smart Contract Architecture](#smart-contract-architecture)
6. [Backend Architecture](#backend-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Testing Guidelines](#testing-guidelines)
9. [Code Conventions](#code-conventions)
10. [Git & CI/CD Practices](#git--cicd-practices)
11. [Common Tasks](#common-tasks)
12. [Security Considerations](#security-considerations)

---

## Project Overview

**Omega Capitals** is a comprehensive DeFi platform integrating:

- **Ω-Score-based governance**: Novel risk calculation formula combining CVaR, PoLE, Psi, and Theta
- **Tokenized financial products**: Ω-Funds (ETF-like), Ω-Bonds (fixed-income), Ω-Futures (derivatives)
- **Payment integration**: LUA-PAY crypto-fiat gateway
- **Autonomous systems**: XI-LUA v2.0 with self-healing, thermodynamic metrics
- **Deployment automation**: MatVerse-Copilot with queue monitoring
- **Multi-platform**: Web app, Telegram bot, Hugging Face Spaces

### Core Formula

```
Ω-Score = (Ψ × Θ) / (CVaR + 1) + PoLE

Where:
- Ψ (Psi): Asset quality metrics
- Θ (Theta): Risk-adjusted returns
- CVaR: Conditional Value at Risk
- PoLE: Proof of Liquidity Efficiency (optimal 70-80% utilization)
```

---

## Repository Structure

This is a **monorepo** containing multiple independent but integrated projects:

```
/home/user/test/
├── contracts/              # Main Solidity contracts
│   ├── core/              # OmegaCapitals.sol, OmegaGovernance.sol, OmegaPool.sol
│   ├── products/          # OmegaFunds.sol, EvidenceNotes.sol
│   └── libraries/         # OmegaScore.sol (risk calculation)
│
├── backend/               # FastAPI Python backend
│   ├── main.py           # Application entry point
│   ├── routes/           # API route handlers
│   │   ├── governance.py # /api/governance endpoints
│   │   ├── funds.py      # /api/funds endpoints
│   │   ├── payments.py   # /api/payments + LUA-PAY webhooks
│   │   └── metrics.py    # /api/metrics dashboard data
│   ├── services/         # Business logic layer
│   │   ├── web3_service.py      # Blockchain interactions
│   │   └── lua_pay_service.py   # Payment gateway integration
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container build
│
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   │   ├── App.tsx              # Main application
│   │   ├── main.tsx             # Entry point
│   │   ├── components/
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   ├── WalletConnect.tsx     # MetaMask integration
│   │   │   ├── LUAPayCheckout.tsx    # Payment flow
│   │   │   └── MetricsChart.tsx      # Recharts visualization
│   ├── vite.config.ts    # Dev server config (port 3000, proxy to :8000)
│   ├── tsconfig.json     # TypeScript config
│   ├── .eslintrc.cjs     # ESLint rules
│   └── package.json      # Dependencies
│
├── scripts/              # Deployment automation
│   ├── deploy-testnet.js    # Deploy to Sepolia/Amoy
│   ├── deploy-mainnet.js    # Production deployment
│   └── verify-contracts.js  # Etherscan verification
│
├── test/                 # Smart contract tests
│   └── OmegaCapitals.test.js
│
├── bot/                  # Telegram bot
│   ├── bot.py           # Main bot logic
│   └── sales_agent.py   # AI-powered sales agent
│
├── xi-lua/              # Autonomous thermodynamic system (Ξ-LUA v2.0)
│   ├── core/
│   │   ├── autoheal/         # lua_autoheal.py, unified_monitor.py
│   │   ├── omniverse/        # omega_gate.py (confidence gating)
│   │   ├── stabilizer/       # stabilizer_recal.py (antifragility)
│   │   ├── metrics/          # thermodynamic_metrics.py
│   │   └── monetization/     # omega_pay.py
│   └── contracts/
│       └── TemporalAnchor.sol  # Proof of Semantic Existence
│
├── matverse-copilot/    # Automated deployment system
│   ├── src/
│   │   ├── monitor.py       # File system queue monitor
│   │   ├── deployer.py      # Multi-platform deployment
│   │   ├── nft_minter.py    # Evidence NFT minting
│   │   └── twitter_bot.py   # Announcement automation
│   └── contracts/
│       └── EvidenceNFT.sol
│
├── omega-capitals/      # Standalone complete deployment (alternative setup)
│   ├── backend/         # Duplicate with TreasuryVault
│   ├── frontend/        # Uses Tailwind CSS
│   └── contracts/       # Extended contracts
│
├── ia-metamask/         # Autonomous Web3 wallet signing
│   ├── ia-metamask.js
│   └── api-server.js
│
├── docs/                # Documentation
├── huggingface/         # Gradio Space integration
├── .github/workflows/   # CI/CD pipelines
│   └── ci-cd.yml
│
├── hardhat.config.js    # Hardhat configuration
├── package.json         # Root npm scripts
├── docker-compose.yml   # Multi-service orchestration
├── .env.example         # Environment template
└── README.md           # User-facing documentation
```

---

## Technology Stack

### Blockchain & Smart Contracts
- **Solidity**: ^0.8.20
- **Hardhat**: 2.19.2 (development framework)
- **OpenZeppelin Contracts**: 5.0.0 (security standards)
- **Networks**:
  - Polygon Mainnet (production)
  - Polygon Amoy Testnet
  - Ethereum Sepolia Testnet
- **Web3 Libraries**: web3.py 6.11.3 (Python), ethers.js 6.9.0 (JavaScript)

### Backend (Python)
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0 (ASGI)
- **Blockchain**: web3.py 6.11.3, eth-account 0.10.0
- **Database**: PostgreSQL (psycopg2-binary 2.9.9), SQLAlchemy 2.0.23
- **Cache**: Redis 5.0.1
- **Validation**: Pydantic 2.5.0
- **HTTP Client**: requests 2.31.0, httpx 0.25.2
- **Testing**: pytest 7.4.3

### Frontend (TypeScript/React)
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.8
- **Language**: TypeScript 5.2.2
- **Routing**: react-router-dom 6.20.0
- **State Management**: @tanstack/react-query 5.12.2
- **Web3**: ethers 6.9.0
- **Charts**: recharts 2.10.3
- **HTTP**: axios 1.6.2
- **Linting**: ESLint 8.55.0

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Security Scanning**: Trivy
- **Deployment**: Hugging Face Spaces, Docker, Vercel-ready

---

## Development Workflows

### Local Development Setup

```bash
# 1. Clone and navigate
git clone <repository-url>
cd test

# 2. Configure environment
cp .env.example .env
# Edit .env with your keys:
#   ALCHEMY_API_KEY, POLYGON_RPC, SEPOLIA_RPC
#   PRIVATE_KEY (wallet with testnet funds)
#   LUA_PAY_API_KEY, LUA_PAY_SECRET
#   TELEGRAM_BOT_TOKEN
#   REDIS_HOST, POSTGRES_URL

# 3. Install dependencies
npm install  # Root (for Hardhat)

cd frontend
npm install

cd ../backend
pip install -r requirements.txt

# 4. Start services (choose one)

# Option A: Docker (recommended)
docker-compose up -d

# Option B: Manual
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Bot (optional)
cd bot && python bot.py
```

### Smart Contract Development

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Coverage report
npx hardhat coverage

# Deploy to testnet
npx hardhat run scripts/deploy-testnet.js --network sepolia
npx hardhat run scripts/deploy-testnet.js --network amoy

# Verify on Etherscan/PolygonScan
npx hardhat run scripts/verify-contracts.js

# Deploy to mainnet (production only)
npx hardhat run scripts/deploy-mainnet.js --network polygon
```

### Backend Development

```bash
cd backend

# Run with hot reload
uvicorn main:app --reload --port 8000

# Run tests
pytest

# Check code quality
black .  # Format (if installed)
flake8   # Lint (if installed)
```

### Frontend Development

```bash
cd frontend

# Dev server (http://localhost:3000)
npm run dev

# Lint
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Smart Contract Architecture

### Core Contracts

#### OmegaCapitals.sol (`contracts/core/`)
**Purpose**: Main ERC20 governance token

**Key Features**:
- Initial supply: 1,000,000,000 OMEGA (18 decimals)
- Omega Score tracking per asset
- Batch score updates for gas efficiency
- Asset whitelisting system
- Token burning mechanism
- Staking functionality (planned)

**Important Functions**:
```solidity
function updateOmegaScore(address asset, uint256 newScore) external onlyOwner
function batchUpdateOmegaScores(address[] calldata assets, uint256[] calldata scores) external onlyOwner
function burn(uint256 amount) external
function getAssetOmegaScore(address asset) external view returns (uint256)
```

**Events**:
```solidity
event OmegaScoreUpdated(address indexed asset, uint256 newScore);
event AssetWhitelisted(address indexed asset);
```

#### OmegaGovernance.sol (`contracts/core/`)
**Purpose**: DAO governance with Omega Score weighted voting

**Key Parameters**:
- Voting period: 3 days (259,200 seconds)
- Quorum requirement: 4% of total supply
- Proposal threshold: 1,000,000 OMEGA
- Omega Score weight: Higher scores = more voting power

**Important Functions**:
```solidity
function createProposal(string memory description, address target, bytes memory data) external returns (uint256)
function vote(uint256 proposalId, bool support) external
function execute(uint256 proposalId) external
function getProposal(uint256 proposalId) external view returns (Proposal memory)
```

**Governance Flow**:
1. User creates proposal (requires threshold)
2. Community votes during voting period
3. Proposal passes if quorum met and majority support
4. Anyone can execute passed proposal after voting ends

#### OmegaPool.sol (`contracts/core/`)
**Purpose**: AMM-style liquidity pool for token swaps

**Key Features**:
- Constant product formula (x * y = k)
- 0.3% swap fee
- LP token minting for liquidity providers
- Price oracle based on reserves

**Important Functions**:
```solidity
function addLiquidity(uint256 amountA, uint256 amountB) external returns (uint256 liquidity)
function removeLiquidity(uint256 liquidity) external returns (uint256 amountA, uint256 amountB)
function swap(address tokenIn, uint256 amountIn, uint256 minAmountOut) external returns (uint256 amountOut)
function getReserves() external view returns (uint256 reserveA, uint256 reserveB)
```

### Product Contracts

#### OmegaFunds.sol (`contracts/products/`)
**Purpose**: Tokenized investment funds with LUA-PAY integration

**Key Features**:
- NAV (Net Asset Value) tracking
- Fiat payment via LUA-PAY invoices
- Share minting based on NAV
- Redemption functionality
- Evidence NFT on investment
- Minimum investment: 10 tokens

**Critical Flow**:
```solidity
// 1. User requests investment via backend
// 2. Backend creates LUA-PAY invoice
// 3. User pays via LUA-PAY
// 4. Webhook confirms payment
// 5. Backend calls processInvestment()
// 6. Shares minted + Evidence NFT issued

function processInvestment(
    address investor,
    uint256 amount,
    string memory invoiceId,
    string memory evidenceHash
) external onlyOwner
```

**Important State**:
```solidity
uint256 public totalAUM;  // Assets Under Management
uint256 public navPerShare;  // Net Asset Value per share
mapping(address => uint256) public investments;
```

#### EvidenceNotes.sol (`contracts/products/`)
**Purpose**: Soulbound NFTs for investment proof

**Key Features**:
- ERC721-based certificates
- Non-transferable (soulbound)
- Immutable evidence hashes
- Product type tracking
- IPFS metadata support

**Important Functions**:
```solidity
function mintEvidence(
    address investor,
    string memory productType,
    uint256 amount,
    string memory evidenceHash
) external onlyOwner returns (uint256)

// Override transfer to prevent (soulbound)
function _beforeTokenTransfer(...) internal override {
    require(from == address(0) || to == address(0), "Soulbound: non-transferable");
}
```

### Library Contracts

#### OmegaScore.sol (`contracts/libraries/`)
**Purpose**: Pure library for risk calculation

**Core Formula Implementation**:
```solidity
function calculateOmegaScore(
    uint256 psi,      // Asset quality (0-10000, scaled 10^4)
    uint256 theta,    // Risk-adjusted returns (0-10000)
    uint256 cvar,     // Conditional Value at Risk (0-10000)
    uint256 pole      // Proof of Liquidity Efficiency (0-10000)
) public pure returns (uint256) {
    // Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
    uint256 numerator = psi * theta;
    uint256 denominator = cvar + 10000; // +1 in scaled terms
    return (numerator / denominator) + pole;
}
```

**Helper Functions**:
```solidity
function calculatePoLE(uint256 utilization) public pure returns (uint256)
// Optimal: 70-80% utilization (7000-8000 in scaled terms)

function calculateCVaR(uint256[] memory returns, uint256 confidenceLevel) public pure returns (uint256)
// Historical return analysis at specified confidence
```

---

## Backend Architecture

### Application Structure

**Entry Point**: `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Omega Capitals API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Web3 initialization
from web3 import Web3
app.state.w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC")))

# Redis caching
import redis
app.state.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
```

### API Routes

#### `/api/governance` (governance.py)
```python
@router.get("/proposals")
async def list_proposals(request: Request):
    """List all governance proposals with caching"""
    # Check Redis cache (TTL: 300s)
    # If miss, query blockchain
    # Return: [{ id, description, proposer, forVotes, againstVotes, executed, deadline }]

@router.post("/proposals")
async def create_proposal(
    description: str,
    target: str,
    data: str,
    wallet: str
):
    """Create new governance proposal"""
    # Validate wallet has threshold tokens
    # Submit transaction
    # Return: { proposalId, txHash }

@router.post("/proposals/{id}/vote")
async def vote_on_proposal(id: int, support: bool, wallet: str):
    """Cast vote on proposal"""
    # Validate wallet hasn't voted
    # Submit vote transaction
    # Return: { txHash, receipt }
```

#### `/api/funds` (funds.py)
```python
@router.get("/")
async def list_funds(request: Request):
    """List all Omega Funds with metrics"""
    # Query OmegaFunds contract
    # Calculate: AUM, NAV, returns, Omega Score
    # Return: [{ name, symbol, aum, nav, omegaScore, returns }]

@router.get("/{fund_id}/performance")
async def get_fund_performance(fund_id: str):
    """Historical performance data for charts"""
    # Query database or cache
    # Return: { dates: [], navs: [], returns: [] }
```

#### `/api/payments` (payments.py)
```python
@router.post("/create-invoice")
async def create_payment_invoice(
    fund_id: str,
    amount: float,
    investor_address: str
):
    """Create LUA-PAY invoice for investment"""
    from services.lua_pay_service import LUAPayService

    service = LUAPayService(
        api_key=os.getenv("LUA_PAY_API_KEY"),
        secret=os.getenv("LUA_PAY_SECRET")
    )

    invoice = service.create_invoice(
        amount=amount,
        currency="USD",
        metadata={"fund_id": fund_id, "investor": investor_address}
    )

    # Return: { invoiceId, paymentUrl, qrCode, expiresAt }

@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle LUA-PAY payment confirmations"""
    # 1. Verify HMAC signature
    # 2. Extract payment data
    # 3. Call OmegaFunds.processInvestment()
    # 4. Mint Evidence NFT
    # 5. Return 200 OK
```

#### `/api/metrics` (metrics.py)
```python
@router.get("/dashboard")
async def get_dashboard_metrics(request: Request):
    """Platform-wide statistics for dashboard"""
    # Calculate:
    # - Total Value Locked (TVL)
    # - Total Users
    # - 24h Volume
    # - Average Omega Score
    # Return: { tvl, users, volume24h, avgOmegaScore }
```

### Service Layer

#### `services/web3_service.py`
```python
class Web3Service:
    def __init__(self, w3: Web3, private_key: str):
        self.w3 = w3
        self.account = Account.from_key(private_key)

    def get_contract(self, address: str, abi: list):
        """Load contract instance"""
        return self.w3.eth.contract(address=address, abi=abi)

    def send_transaction(self, contract_function, value: int = 0):
        """Sign and send transaction with gas estimation"""
        # Build transaction
        # Estimate gas
        # Sign with private key
        # Send and wait for receipt
        # Return: tx_hash, receipt

    def get_omega_score(self, asset: str) -> int:
        """Query Omega Score for asset"""
        contract = self.get_contract(OMEGA_CAPITALS_ADDRESS, ABI)
        return contract.functions.getAssetOmegaScore(asset).call()
```

#### `services/lua_pay_service.py`
```python
class LUAPayService:
    BASE_URL = "https://api.luapay.io/v1"

    def create_invoice(self, amount: float, currency: str, metadata: dict):
        """Create payment invoice"""
        payload = {
            "amount": amount,
            "currency": currency,
            "metadata": metadata,
            "webhook_url": os.getenv("LUA_PAY_WEBHOOK_URL")
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(f"{self.BASE_URL}/invoices", json=payload, headers=headers)
        return response.json()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC-SHA256 webhook signature"""
        import hmac
        import hashlib

        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
```

---

## Frontend Architecture

### Component Structure

#### `App.tsx` - Main Application
```typescript
function App() {
  const [account, setAccount] = useState<string | null>(null);
  const [provider, setProvider] = useState<ethers.BrowserProvider | null>(null);

  return (
    <div className="App">
      <WalletConnect onConnect={(acc, prov) => {
        setAccount(acc);
        setProvider(prov);
      }} />

      {account ? (
        <Dashboard account={account} provider={provider} />
      ) : (
        <WelcomePage />
      )}
    </div>
  );
}
```

#### `components/WalletConnect.tsx` - MetaMask Integration
```typescript
const connectWallet = async () => {
  if (!window.ethereum) {
    alert("Please install MetaMask!");
    return;
  }

  const provider = new ethers.BrowserProvider(window.ethereum);
  const accounts = await provider.send("eth_requestAccounts", []);
  const signer = await provider.getSigner();

  // Get balance
  const balance = await provider.getBalance(accounts[0]);

  onConnect(accounts[0], provider);
};

// Auto-reconnect on page load
useEffect(() => {
  if (window.ethereum) {
    window.ethereum.request({ method: 'eth_accounts' })
      .then((accounts: string[]) => {
        if (accounts.length > 0) {
          connectWallet();
        }
      });
  }
}, []);
```

#### `components/Dashboard.tsx` - Main Dashboard
```typescript
function Dashboard({ account, provider }: Props) {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [funds, setFunds] = useState<Fund[]>([]);

  useEffect(() => {
    // Fetch dashboard metrics
    axios.get('/api/metrics/dashboard').then(res => setMetrics(res.data));

    // Fetch available funds
    axios.get('/api/funds/').then(res => setFunds(res.data));
  }, []);

  return (
    <div className="dashboard">
      <MetricsGrid metrics={metrics} />
      <PerformanceChart />
      <FundsCatalog funds={funds} onInvest={handleInvest} />
    </div>
  );
}
```

#### `components/LUAPayCheckout.tsx` - Payment Flow
```typescript
function LUAPayCheckout({ fundId, amount, investorAddress }: Props) {
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [status, setStatus] = useState<'pending' | 'paid' | 'expired'>('pending');

  const initiatePayment = async () => {
    const response = await axios.post('/api/payments/create-invoice', {
      fund_id: fundId,
      amount,
      investor_address: investorAddress
    });

    setInvoice(response.data);

    // Poll for payment status
    const interval = setInterval(async () => {
      const statusRes = await axios.get(`/api/payments/${response.data.invoiceId}/status`);
      setStatus(statusRes.data.status);

      if (statusRes.data.status !== 'pending') {
        clearInterval(interval);
      }
    }, 5000);
  };

  return (
    <div className="checkout">
      {invoice && (
        <>
          <QRCode value={invoice.paymentUrl} />
          <p>Pay {amount} USD via LUA-PAY</p>
          <a href={invoice.paymentUrl} target="_blank">Open Payment Page</a>
        </>
      )}
    </div>
  );
}
```

### Styling Conventions

**Approach**: CSS-in-JS with inline styles

```typescript
const styles = {
  container: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    minHeight: '100vh',
    padding: '20px'
  },
  card: {
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
    backdropFilter: 'blur(10px)'
  },
  button: {
    background: '#667eea',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
    }
  }
};
```

**Theme Colors**:
- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (orange)
- Error: `#ef4444` (red)

---

## Testing Guidelines

### Smart Contract Tests

**Location**: `test/OmegaCapitals.test.js`

**Pattern**: Hardhat + Chai assertions

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("OmegaCapitals", function () {
  let omega, governance, pool, evidenceNotes;
  let owner, addr1, addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();

    // Deploy contracts
    const Omega = await ethers.getContractFactory("OmegaCapitals");
    omega = await Omega.deploy();
    await omega.deployed();
  });

  it("Should have correct initial supply", async function () {
    const totalSupply = await omega.totalSupply();
    expect(totalSupply).to.equal(ethers.utils.parseEther("1000000000"));
  });

  it("Should update Omega Score", async function () {
    const asset = addr1.address;
    const score = 8500; // 0.85 in scaled terms

    await expect(omega.updateOmegaScore(asset, score))
      .to.emit(omega, "OmegaScoreUpdated")
      .withArgs(asset, score);

    expect(await omega.getAssetOmegaScore(asset)).to.equal(score);
  });

  it("Should prevent non-owner from updating scores", async function () {
    await expect(
      omega.connect(addr1).updateOmegaScore(addr2.address, 5000)
    ).to.be.revertedWith("Ownable: caller is not the owner");
  });
});
```

**Run tests**:
```bash
npx hardhat test                    # All tests
npx hardhat test test/Omega*.test.js  # Specific file
npx hardhat coverage                # Coverage report
```

### Backend Tests

**Location**: `backend/test_main.py`

**Pattern**: pytest with FastAPI TestClient

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_dashboard_metrics():
    response = client.get("/api/metrics/dashboard")
    assert response.status_code == 200

    data = response.json()
    assert "tvl" in data
    assert "users" in data
    assert "volume24h" in data
    assert "avgOmegaScore" in data

def test_create_invoice():
    payload = {
        "fund_id": "omega-fund-1",
        "amount": 1000.0,
        "investor_address": "0x1234..."
    }

    response = client.post("/api/payments/create-invoice", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "invoiceId" in data
    assert "paymentUrl" in data
```

**Run tests**:
```bash
cd backend
pytest                    # All tests
pytest -v                 # Verbose
pytest test_main.py::test_health_check  # Specific test
```

### Frontend Tests

**Location**: `frontend/src/__tests__/`

**Pattern**: Vite test runner (limited coverage currently)

**Linting**:
```bash
cd frontend
npm run lint  # ESLint check
```

---

## Code Conventions

### Naming Conventions

**Smart Contracts** (Solidity):
- Contracts: `PascalCase` (e.g., `OmegaCapitals`, `EvidenceNotes`)
- Functions: `camelCase` (e.g., `updateOmegaScore`, `mintEvidence`)
- State variables: `camelCase` (e.g., `totalSupply`, `navPerShare`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MIN_INVESTMENT`, `VOTING_PERIOD`)
- Events: `PascalCase` (e.g., `OmegaScoreUpdated`, `ProposalCreated`)

**Backend** (Python):
- Files: `snake_case` (e.g., `lua_pay_service.py`, `web3_service.py`)
- Classes: `PascalCase` (e.g., `Web3Service`, `LUAPayService`)
- Functions: `snake_case` (e.g., `create_invoice`, `get_omega_score`)
- Variables: `snake_case` (e.g., `tx_hash`, `invoice_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `BASE_URL`, `API_KEY`)

**Frontend** (TypeScript):
- Files: `PascalCase.tsx` for components (e.g., `Dashboard.tsx`)
- Components: `PascalCase` (e.g., `WalletConnect`, `MetricsChart`)
- Functions: `camelCase` (e.g., `connectWallet`, `handleInvest`)
- Variables: `camelCase` (e.g., `account`, `provider`)
- Types/Interfaces: `PascalCase` (e.g., `MetricsData`, `FundInfo`)

### Code Style

**Solidity**:
- Use OpenZeppelin base contracts (ERC20, Ownable, ReentrancyGuard)
- Emit events for all state changes
- Use `calldata` for external array parameters (gas optimization)
- Add NatSpec comments for public functions
- Group by: state variables, events, modifiers, constructor, external, public, internal, private

**Python**:
- Follow PEP 8
- Type hints for function signatures
- Docstrings for classes and complex functions
- Use Pydantic models for request/response validation
- Async/await for I/O operations

**TypeScript**:
- Strict mode: **disabled** (`tsconfig.json`: `"strict": false`)
- Use interfaces for prop types
- Functional components with hooks (no class components)
- Explicit return types for complex functions
- ESLint rules: max 50 warnings allowed

### Security Patterns

**Smart Contracts**:
```solidity
// ✅ GOOD: ReentrancyGuard for external calls
function withdraw() external nonReentrant {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;  // Update state before external call
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}

// ✅ GOOD: Access control
modifier onlyGovernance() {
    require(msg.sender == governance, "Not governance");
    _;
}

// ✅ GOOD: Input validation
require(amount > 0, "Amount must be positive");
require(recipient != address(0), "Invalid recipient");

// ❌ BAD: Missing checks
function transfer(address to, uint256 amount) external {
    balances[to] += amount;  // Missing: sender balance check, overflow check
}
```

**Backend**:
```python
# ✅ GOOD: Webhook signature verification
def verify_webhook(payload: bytes, signature: str) -> bool:
    expected = hmac.new(SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# ✅ GOOD: Input validation with Pydantic
class InvoiceRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount must be positive")
    investor_address: str = Field(regex="^0x[a-fA-F0-9]{40}$")

# ✅ GOOD: Environment variables for secrets
API_KEY = os.getenv("LUA_PAY_API_KEY")
if not API_KEY:
    raise ValueError("LUA_PAY_API_KEY not set")

# ❌ BAD: Hardcoded secrets
API_KEY = "sk_live_123456789"  # NEVER do this
```

**Frontend**:
```typescript
// ✅ GOOD: Never expose private keys in frontend
// Use MetaMask for signing

// ✅ GOOD: Validate user input
const amount = parseFloat(input);
if (isNaN(amount) || amount <= 0) {
  alert("Invalid amount");
  return;
}

// ✅ GOOD: Handle errors gracefully
try {
  const tx = await contract.invest(amount);
  await tx.wait();
} catch (error) {
  console.error("Transaction failed:", error);
  alert("Investment failed. Please try again.");
}

// ❌ BAD: Trusting user input without validation
const amount = parseFloat(userInput);  // Could be NaN, Infinity, negative
await contract.invest(amount);
```

### Gas Optimization Patterns

```solidity
// ✅ GOOD: Batch operations
function batchUpdateOmegaScores(
    address[] calldata assets,
    uint256[] calldata scores
) external onlyOwner {
    require(assets.length == scores.length, "Length mismatch");
    for (uint256 i = 0; i < assets.length; i++) {
        _updateOmegaScore(assets[i], scores[i]);
    }
}

// ✅ GOOD: Use calldata for read-only arrays
function process(uint256[] calldata values) external { /* ... */ }

// ✅ GOOD: Cache storage reads
uint256 supply = totalSupply;  // Single SLOAD
for (uint256 i = 0; i < 100; i++) {
    // Use 'supply' instead of reading 'totalSupply' 100 times
}

// ❌ BAD: Repeated storage reads in loop
for (uint256 i = 0; i < 100; i++) {
    if (totalSupply > threshold) { /* ... */ }  // 100 SLOADs
}
```

---

## Git & CI/CD Practices

### Branch Strategy

**Main Branches**:
- `main`: Production-ready code, protected
- `develop`: Integration branch for features (if used)

**Feature Branches**:
- Pattern: `claude/claude-md-<random>-<session-id>`
- Example: `claude/claude-md-miazrgai9yyoznsh-01VYBahhS6Z7KWGmjnksjvgw`
- **IMPORTANT**: Must start with `claude/` and end with matching session ID, otherwise push fails with 403

### Commit Messages

**Format**: Follow Conventional Commits with emoji prefixes

```
<emoji> <type>: <description>

Examples:
✨ feat: Add Omega Score calculation to funds API
🐛 fix: Resolve MetaMask connection timeout issue
🔧 chore: Update ESLint rules to allow builds
📝 docs: Add API documentation for governance endpoints
♻️ refactor: Simplify Web3 service initialization
🧪 test: Add unit tests for LUA-PAY webhook verification
🔒 security: Fix CSRF vulnerability in payment webhook
⬆️ upgrade: Update actions/upload-artifact from v3 to v4
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `chore`: Maintenance tasks
- `docs`: Documentation
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `security`: Security improvements
- `upgrade`: Dependency updates

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/ci-cd.yml`)

**Triggers**:
- Push to: `main`, `develop`, `claude/*`
- Pull requests to: `main`, `develop`

**Jobs**:

1. **contracts** - Smart Contract Testing
   - Compile with Hardhat
   - Run test suite
   - Generate coverage (non-blocking)

2. **backend** - Python API Testing
   - Start PostgreSQL and Redis services
   - Install dependencies with pip cache
   - Run pytest

3. **frontend** - React Build
   - Install dependencies with npm cache
   - Run ESLint (max 50 warnings)
   - Build TypeScript

4. **security** - Vulnerability Scanning
   - Trivy filesystem scan
   - Non-blocking (continue on errors)

5. **docker** - Container Build
   - Only on `main` branch
   - Build backend and frontend images
   - Push to registry (if configured)

6. **deploy-hf** - Hugging Face Spaces
   - Deploy to HF Spaces on `main`
   - OAuth2 authentication

**Important Notes**:
- Tests run in parallel for speed
- Coverage is non-blocking (won't fail build)
- Docker builds only on main branch
- All jobs must pass for PR merge

### Push & Pull with Retry Logic

**For git push**:
```bash
# Always use -u flag for new branches
git push -u origin claude/claude-md-miazrgai9yyoznsh-01VYBahhS6Z7KWGmjnksjvgw

# If network fails, retry up to 4 times with exponential backoff:
# Attempt 1 -> Wait 2s -> Attempt 2 -> Wait 4s -> Attempt 3 -> Wait 8s -> Attempt 4
```

**For git fetch/pull**:
```bash
# Prefer specific branches
git fetch origin main

# Retry up to 4 times on network failures
# Same exponential backoff: 2s, 4s, 8s, 16s
```

---

## Common Tasks

### Adding a New Smart Contract

```bash
# 1. Create contract in contracts/
touch contracts/products/NewProduct.sol

# 2. Implement with OpenZeppelin bases
# contracts/products/NewProduct.sol
# SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NewProduct is ERC20, Ownable {
    constructor() ERC20("New Product", "NPD") {
        _mint(msg.sender, 1000000 * 10**decimals());
    }
}

# 3. Add to deployment script
# Edit scripts/deploy-testnet.js
const NewProduct = await ethers.getContractFactory("NewProduct");
const newProduct = await NewProduct.deploy();
await newProduct.deployed();
console.log("NewProduct deployed to:", newProduct.address);

# 4. Write tests
# Edit test/OmegaCapitals.test.js or create test/NewProduct.test.js

# 5. Compile and test
npx hardhat compile
npx hardhat test

# 6. Deploy to testnet
npx hardhat run scripts/deploy-testnet.js --network sepolia

# 7. Update backend with new contract address and ABI
# Edit backend/.env
NEW_PRODUCT_ADDRESS=0x...

# 8. Create API routes if needed
# backend/routes/new_product.py
```

### Adding a New API Endpoint

```bash
# 1. Define route in backend/routes/
# backend/routes/analytics.py
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/performance/{fund_id}")
async def get_fund_performance(fund_id: str, request: Request):
    """Get historical performance for a fund"""
    # Query database or blockchain
    return {"fund_id": fund_id, "data": [...]}

# 2. Register router in main.py
from routes import analytics
app.include_router(analytics.router)

# 3. Write tests
# backend/test_analytics.py
def test_get_fund_performance():
    response = client.get("/api/analytics/performance/fund-1")
    assert response.status_code == 200

# 4. Update frontend API client
# frontend/src/api/analytics.ts
export const getFundPerformance = async (fundId: string) => {
  const response = await axios.get(`/api/analytics/performance/${fundId}`);
  return response.data;
};

# 5. Test locally
cd backend && uvicorn main:app --reload
# In another terminal:
curl http://localhost:8000/api/analytics/performance/fund-1
```

### Adding a New React Component

```bash
# 1. Create component file
# frontend/src/components/PortfolioView.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Portfolio {
  investments: Investment[];
  totalValue: number;
}

export function PortfolioView({ account }: { account: string }) {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);

  useEffect(() => {
    axios.get(`/api/portfolio/${account}`)
      .then(res => setPortfolio(res.data));
  }, [account]);

  return (
    <div style={styles.container}>
      <h2>My Portfolio</h2>
      {portfolio && (
        <div>
          <p>Total Value: ${portfolio.totalValue.toLocaleString()}</p>
          {portfolio.investments.map(inv => (
            <InvestmentCard key={inv.id} investment={inv} />
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: '24px',
    background: 'white',
    borderRadius: '12px'
  }
};

# 2. Import and use in App.tsx
import { PortfolioView } from './components/PortfolioView';

// In App.tsx:
<PortfolioView account={account} />

# 3. Test locally
cd frontend && npm run dev
# Visit http://localhost:3000
```

### Deploying to Production

```bash
# 1. Ensure .env has production values
POLYGON_RPC=https://polygon-rpc.com
PRIVATE_KEY=<production-wallet-key>
LUA_PAY_API_KEY=<production-key>

# 2. Deploy contracts to mainnet
npx hardhat run scripts/deploy-mainnet.js --network polygon

# 3. Verify contracts on PolygonScan
npx hardhat run scripts/verify-contracts.js

# 4. Update backend environment
# Update .env or set environment variables in deployment platform

# 5. Build frontend
cd frontend
npm run build
# Output in frontend/dist/

# 6. Deploy via Docker
docker-compose -f docker-compose.prod.yml up -d

# 7. Monitor logs
docker-compose logs -f backend
docker-compose logs -f frontend

# 8. Verify deployment
curl https://your-domain.com/health
curl https://your-domain.com/api/metrics/dashboard
```

---

## Security Considerations

### Environment Variables

**Required Variables** (`.env`):
```env
# Blockchain
ALCHEMY_API_KEY=your_alchemy_key
POLYGON_RPC=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=your_wallet_private_key  # KEEP SECRET - use hardware wallet in production

# LUA-PAY
LUA_PAY_API_KEY=your_lua_pay_key
LUA_PAY_SECRET=your_lua_pay_secret
LUA_PAY_WEBHOOK_URL=https://your-backend.com/api/payments/webhook

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_token

# Database
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_URL=postgresql://postgres:secret@localhost:5432/omega
```

**Never commit**:
- `.env` (use `.env.example` as template)
- Private keys
- API secrets
- Database credentials

### Smart Contract Security

**Critical Checks**:
1. **Reentrancy**: Use `ReentrancyGuard` from OpenZeppelin
2. **Access Control**: `onlyOwner`, `onlyGovernance` modifiers
3. **Integer Overflow**: Solidity 0.8.x has built-in checks
4. **Front-running**: Consider using commit-reveal for sensitive operations
5. **Oracle Manipulation**: Validate external data sources
6. **Gas Limits**: Test with realistic data sizes

**Audit Checklist**:
- [ ] All external calls use `nonReentrant`
- [ ] State changes before external calls (checks-effects-interactions)
- [ ] Input validation on all parameters
- [ ] Events emitted for all state changes
- [ ] Access control on privileged functions
- [ ] No hardcoded addresses (use constructor parameters)
- [ ] Pausable mechanism for emergencies

### Backend Security

**Critical Practices**:
1. **CORS**: Whitelist allowed origins in production
   ```python
   allow_origins=["https://yourdomain.com"]  # Not "*" in production
   ```

2. **Webhook Verification**: Always verify HMAC signatures
   ```python
   if not verify_webhook_signature(payload, signature):
       raise HTTPException(status_code=401, detail="Invalid signature")
   ```

3. **Rate Limiting**: Implement for public endpoints
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)

   @app.get("/api/metrics")
   @limiter.limit("100/minute")
   async def metrics():
       ...
   ```

4. **Input Validation**: Use Pydantic models
   ```python
   class InvestmentRequest(BaseModel):
       amount: float = Field(gt=0, le=1000000)
       address: str = Field(regex="^0x[a-fA-F0-9]{40}$")
   ```

5. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)

6. **Private Key Management**:
   - Development: Use `.env` with test wallets
   - Production: Use hardware wallets, KMS, or secure vaults
   - **Never log private keys**

### Frontend Security

**Critical Practices**:
1. **Never expose secrets**: No API keys, private keys in frontend code
2. **Use MetaMask for signing**: Never handle private keys directly
3. **Validate all inputs**: Check amounts, addresses before transactions
4. **HTTPS only**: Enforce in production
5. **Content Security Policy**: Add CSP headers
6. **XSS Prevention**: React escapes by default, but be careful with `dangerouslySetInnerHTML`

### Database Security

**PostgreSQL**:
- Use strong passwords
- Enable SSL connections in production
- Limit database user permissions (no DROP, CREATE in app user)
- Regular backups

**Redis**:
- Enable authentication (`requirepass` in redis.conf)
- Bind to localhost unless needed externally
- Use Redis ACLs in production
- Set TTL on all cached data to prevent stale data

---

## XI-LUA Autonomous System

### Overview
XI-LUA v2.0 is an autonomous thermodynamic system with self-healing capabilities.

**Key Components**:
1. **Lua-AutoHeal**: Ephemeral key rotation, unified monitoring, kill switches
2. **Ω-GATE**: Confidence formula gating system (Ω ≥ 0.90 threshold)
3. **Stabilizer**: Antifragility engine with attack detection
4. **TemporalAnchor**: Blockchain-based Proof of Semantic Existence

### Development Guidelines

**When modifying XI-LUA**:
1. **Maintain dimensional consistency** in thermodynamic formulas
2. **Preserve confidence threshold**: Ω ≥ 0.90 for critical operations
3. **Test kill switches**: Ensure emergency shutdown works
4. **Verify Merkle chains**: Immutability is critical
5. **Respect key rotation**: 5-minute ephemeral key TTL

**Testing**:
```bash
cd xi-lua
python core/autoheal/test_autoheal.py
bash demo_autoheal.sh
```

---

## MatVerse-Copilot Deployment System

### Overview
Automated multi-platform deployment system with queue monitoring.

**Workflow**:
1. User drops file in `~/deploy-queue/`
2. Monitor detects new file
3. Deployer pushes to GitHub, HuggingFace, arXiv
4. NFT minter creates Evidence NFT on blockchain
5. Twitter bot announces deployment

**Development Guidelines**:
- Queue directory: `~/deploy-queue/`
- Supported file types: `.py`, `.ipynb`, `.md`, `.tex`
- Evidence NFT metadata stored on IPFS
- Twitter announcements use API v2

---

## Additional Resources

### Documentation
- **Whitepaper**: `docs/whitepaper.md` - Technical details of Omega Score
- **Pitch Deck**: `docs/pitch-deck.md` - Business overview
- **XI-LUA Summary**: `XI-LUA-v2-SUMMARY.md` - Autonomous system details

### External Links
- **OpenZeppelin Docs**: https://docs.openzeppelin.com/contracts/
- **Hardhat Docs**: https://hardhat.org/getting-started/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **ethers.js Docs**: https://docs.ethers.org/v6/
- **LUA-PAY API**: https://docs.luapay.io/ (if available)

### Contact & Support
- **Issues**: Submit via GitHub Issues
- **Pull Requests**: Follow standard fork-and-pull workflow
- **Questions**: Check documentation first, then open discussion

---

## Changelog

### 2025-11-23
- Initial CLAUDE.md creation
- Comprehensive codebase analysis
- Documentation of all major systems
- Development workflow guidelines
- Security best practices

---

**This document should be updated whenever significant architectural changes are made to the codebase.**
