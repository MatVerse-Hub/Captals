"""
Metrics Routes - Omega Score and analytics endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
import os

from services.web3_service import Web3Service

router = APIRouter()


@router.get("/omega-score/{asset_address}")
async def get_omega_score(asset_address: str, app_request: Request):
    """
    Get Omega Score for a specific asset
    """
    try:
        w3 = app_request.app.state.w3
        web3_service = Web3Service(w3)

        score = web3_service.calculate_omega_score(asset_address)

        return {
            "asset": asset_address,
            "omega_score": score,
            "components": {
                "psi": 85,
                "theta": 92,
                "cvar": 12,
                "pole": 88
            },
            "rating": "A+" if score > 8000 else "A" if score > 7000 else "B+"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pool/{pool_address}")
async def get_pool_metrics(pool_address: str, app_request: Request):
    """
    Get metrics for a liquidity pool
    """
    try:
        w3 = app_request.app.state.w3
        web3_service = Web3Service(w3)

        reserves = web3_service.get_pool_reserves(pool_address)

        return {
            "pool_address": pool_address,
            "reserves": reserves,
            "tvl": reserves.get("reserveA", 0) + reserves.get("reserveB", 0),
            "volume_24h": 125000,
            "fees_24h": 375,
            "apr": 12.5,
            "omega_score": 8700
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_metrics(app_request: Request):
    """
    Get overall platform metrics for dashboard
    """
    try:
        metrics = {
            "tvl": 4700000,
            "total_users": 1250,
            "total_transactions": 8500,
            "volume_24h": 450000,
            "avg_omega_score": 8500,
            "active_funds": 2,
            "active_proposals": 3,
            "recent_investments": [
                {
                    "investor": "0x742d35...5f0bEb",
                    "fund": "Omega Growth Fund",
                    "amount": 1000,
                    "timestamp": 1700150000
                },
                {
                    "investor": "0x8626f6...C9C1199",
                    "fund": "Omega Stable Fund",
                    "amount": 5000,
                    "timestamp": 1700148000
                }
            ],
            "top_performers": [
                {
                    "fund": "Omega Growth Fund",
                    "performance_7d": 2.3,
                    "omega_score": 8500
                },
                {
                    "fund": "Omega Stable Fund",
                    "performance_7d": 0.6,
                    "omega_score": 9200
                }
            ]
        }

        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/historical")
async def get_historical_data(
    metric: str,
    period: str = "7d",
    app_request: Request
):
    """
    Get historical data for charts
    """
    try:
        # Mock time series data
        data_points = []

        if metric == "tvl":
            base = 4500000
            for i in range(7):
                data_points.append({
                    "timestamp": 1700000000 + (i * 86400),
                    "value": base + (i * 25000) + (i % 2 * 10000)
                })
        elif metric == "omega_score":
            base = 8400
            for i in range(7):
                data_points.append({
                    "timestamp": 1700000000 + (i * 86400),
                    "value": base + (i * 10) + (i % 3 * 5)
                })

        return {
            "metric": metric,
            "period": period,
            "data": data_points
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
