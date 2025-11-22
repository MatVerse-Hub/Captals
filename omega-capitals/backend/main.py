from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from web3 import Web3
from typing import Optional, List
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Omega Capitals API",
    description="Portfolio Risk Management & NFT Evidence System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Web3 Setup
RPC_URL = os.getenv("POLYGON_RPC_URL", "https://rpc-amoy.polygon.technology")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load contract ABIs and addresses
def load_contract(name: str):
    """Load contract ABI and address"""
    try:
        with open(f"abis/{name}.json") as f:
            abi = json.load(f)

        with open("abis/deployment-amoy.json") as f:
            deployment = json.load(f)

        address = deployment["contracts"][name]
        return w3.eth.contract(address=address, abi=abi)
    except Exception as e:
        print(f"⚠️  Could not load {name}: {e}")
        return None

# Load contracts
evidence_notes = load_contract("EvidenceNotes")
omega_pool = load_contract("OmegaPool")
treasury_vault = load_contract("TreasuryVault")
omega_governance = load_contract("OmegaGovernance")

# Pydantic Models
class OmegaScoreInput(BaseModel):
    cvar: float = Field(..., ge=0, le=1, description="Conditional Value at Risk (0-1)")
    beta: float = Field(..., ge=0, le=1, description="Beta coefficient (0-1)")
    err5m: float = Field(..., ge=0, le=1, description="Max 5-min error (0-1)")
    idem: float = Field(..., ge=0, le=1, description="Idempotency score (0-1)")

class MintNFTRequest(BaseModel):
    to: str = Field(..., description="Recipient wallet address")
    uri: str = Field(..., description="IPFS/Arweave URI")

class DepositRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in wei")

class StrategyRequest(BaseModel):
    manager: str
    cvar: float
    beta: float
    err5m: float
    idem: float

# Helper functions
def to_wei(value: float) -> int:
    """Convert float to wei (1e18 precision)"""
    return int(value * 1e18)

def from_wei(value: int) -> float:
    """Convert wei to float"""
    return value / 1e18

def compute_omega_score(cvar: float, beta: float, err5m: float, idem: float) -> float:
    """Compute Ω-Score: 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem"""
    omega = (
        0.4 * (1 - cvar) +
        0.3 * (1 - beta) +
        0.2 * (1 - err5m) +
        0.1 * idem
    )
    return round(omega * 1000)  # Scale to 0-1000

def get_risk_tier(omega: float) -> str:
    """Get risk tier from Ω-Score"""
    if omega >= 800:
        return "Low Risk"
    elif omega >= 600:
        return "Medium Risk"
    elif omega >= 400:
        return "High Risk"
    else:
        return "Critical Risk"

# Routes
@app.get("/")
def root():
    return {
        "name": "Omega Capitals API",
        "version": "1.0.0",
        "network": "Polygon Amoy Testnet",
        "contracts": {
            "EvidenceNotes": evidence_notes.address if evidence_notes else None,
            "OmegaPool": omega_pool.address if omega_pool else None,
            "TreasuryVault": treasury_vault.address if treasury_vault else None,
            "OmegaGovernance": omega_governance.address if omega_governance else None
        }
    }

@app.post("/api/omega/compute")
def compute_omega(data: OmegaScoreInput):
    """Compute Ω-Score from risk metrics"""
    omega = compute_omega_score(data.cvar, data.beta, data.err5m, data.idem)
    tier = get_risk_tier(omega)

    return {
        "omega_score": omega,
        "risk_tier": tier,
        "metrics": {
            "cvar": data.cvar,
            "beta": data.beta,
            "err5m": data.err5m,
            "idem": data.idem
        },
        "breakdown": {
            "cvar_contribution": round(0.4 * (1 - data.cvar) * 1000, 2),
            "beta_contribution": round(0.3 * (1 - data.beta) * 1000, 2),
            "err5m_contribution": round(0.2 * (1 - data.err5m) * 1000, 2),
            "idem_contribution": round(0.1 * data.idem * 1000, 2)
        }
    }

@app.post("/api/nft/mint")
def mint_nft(data: MintNFTRequest):
    """Mint Evidence NFT"""
    if not evidence_notes:
        raise HTTPException(status_code=503, detail="EvidenceNotes contract not loaded")

    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(os.getenv("PUBLIC_KEY"))
        tx = evidence_notes.functions.mint(
            w3.to_checksum_address(data.to),
            data.uri
        ).build_transaction({
            "from": os.getenv("PUBLIC_KEY"),
            "nonce": nonce,
            "gas": 300_000,
            "gasPrice": w3.to_wei("2", "gwei")
        })

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, os.getenv("PRIVATE_KEY"))
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash.hex()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mint failed: {str(e)}")

@app.get("/api/nft/{token_id}")
def get_nft(token_id: int):
    """Get NFT metadata"""
    if not evidence_notes:
        raise HTTPException(status_code=503, detail="Contract not loaded")

    try:
        owner = evidence_notes.functions.ownerOf(token_id).call()
        uri = evidence_notes.functions.tokenURI(token_id).call()

        return {
            "token_id": token_id,
            "owner": owner,
            "uri": uri
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"NFT not found: {str(e)}")

@app.post("/api/pool/add-strategy")
def add_strategy(data: StrategyRequest):
    """Add strategy to OmegaPool"""
    if not omega_pool:
        raise HTTPException(status_code=503, detail="OmegaPool not loaded")

    try:
        omega = compute_omega_score(data.cvar, data.beta, data.err5m, data.idem)

        if omega < 600:
            raise HTTPException(status_code=400, detail=f"Ω-Score {omega} below minimum 600")

        # Build transaction
        nonce = w3.eth.get_transaction_count(os.getenv("PUBLIC_KEY"))
        tx = omega_pool.functions.addStrategy(
            w3.to_checksum_address(data.manager),
            to_wei(data.cvar),
            to_wei(data.beta),
            to_wei(data.err5m),
            to_wei(data.idem)
        ).build_transaction({
            "from": os.getenv("PUBLIC_KEY"),
            "nonce": nonce,
            "gas": 500_000,
            "gasPrice": w3.to_wei("2", "gwei")
        })

        signed_tx = w3.eth.account.sign_transaction(tx, os.getenv("PRIVATE_KEY"))
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return {
            "success": True,
            "omega_score": omega,
            "tx_hash": tx_hash.hex(),
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash.hex()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Add strategy failed: {str(e)}")

@app.get("/api/pool/tvl")
def get_pool_tvl():
    """Get OmegaPool Total Value Locked"""
    if not omega_pool:
        raise HTTPException(status_code=503, detail="OmegaPool not loaded")

    try:
        tvl = omega_pool.functions.getTVL().call()
        return {
            "tvl": from_wei(tvl),
            "tvl_wei": tvl,
            "currency": "USDC"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pool/strategy/{strategy_id}")
def get_strategy(strategy_id: int):
    """Get strategy details"""
    if not omega_pool:
        raise HTTPException(status_code=503, detail="OmegaPool not loaded")

    try:
        strategy = omega_pool.functions.strategies(strategy_id).call()

        return {
            "id": strategy[0],
            "manager": strategy[1],
            "omega_score": strategy[2],
            "allocated_capital": from_wei(strategy[3]),
            "current_value": from_wei(strategy[4]),
            "last_update": strategy[5],
            "active": strategy[6]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {str(e)}")

@app.get("/api/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "web3_connected": w3.is_connected(),
        "contracts_loaded": {
            "EvidenceNotes": evidence_notes is not None,
            "OmegaPool": omega_pool is not None,
            "TreasuryVault": treasury_vault is not None,
            "OmegaGovernance": omega_governance is not None
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
