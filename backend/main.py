"""
Captals / Omega Capitals Backend - FastAPI Application
Main entry point for the API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
import redis
import os
from dotenv import load_dotenv

from routes.governance import router as governance_router
from routes.funds import router as funds_router
from routes.payments import router as payments_router
from routes.metrics import router as metrics_router
from routes.captals import router as captals_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Captals / Omega Capitals API",
    description=(
        "Omega Capitals DeFi surface plus the Captals multidimensional "
        "value/resource metabolism layer"
    ),
    version="1.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Web3 connection
POLYGON_RPC = os.getenv("POLYGON_RPC", "https://rpc.ankr.com/polygon_amoy")
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Store globally for access in routes
app.state.w3 = w3
app.state.redis = redis_client

# Legacy Ω-Capitals routers remain intact.
app.include_router(governance_router, prefix="/api/governance", tags=["Governance"])
app.include_router(funds_router, prefix="/api/funds", tags=["Funds"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(metrics_router, prefix="/api/metrics", tags=["Metrics"])

# Canonical Captals metabolism layer composes the legacy surface rather than
# replacing or reinterpreting it.
app.include_router(captals_router, prefix="/api/captals", tags=["Captals"])


@app.get("/")
async def root():
    """Root endpoint - API status and lineage."""
    return {
        # Kept for backward compatibility with the historical API/tests.
        "message": "Omega Capitals API",
        "canonical_name": "Captals",
        "legacy_surface": "Omega Capitals (Ω-Capitals)",
        "version": "1.1.0",
        "status": "operational",
        "blockchain": {
            "connected": w3.is_connected(),
            "chain_id": w3.eth.chain_id if w3.is_connected() else None
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Web3 connection
        web3_connected = w3.is_connected()

        # Check Redis connection
        redis_connected = redis_client.ping()

        return {
            "status": "healthy" if web3_connected and redis_connected else "degraded",
            "services": {
                "web3": "connected" if web3_connected else "disconnected",
                "redis": "connected" if redis_connected else "disconnected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Captals / Omega Capitals API starting up...")
    print(f"📡 Blockchain: {'Connected' if w3.is_connected() else 'Disconnected'}")
    print(f"💾 Redis: {'Connected' if redis_client.ping() else 'Disconnected'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Captals / Omega Capitals API shutting down...")
    redis_client.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
