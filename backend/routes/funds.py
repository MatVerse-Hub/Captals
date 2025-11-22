"""
Funds Routes - Omega Funds management endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import os

from services.web3_service import Web3Service

router = APIRouter()


class InvestmentRequest(BaseModel):
    fund_address: str
    amount: float
    investor_address: str


@router.get("/")
async def get_funds(app_request: Request):
    """
    Get list of available Omega Funds
    """
    try:
        # Mock data (in production, fetch from contract registry)
        funds = [
            {
                "address": "0x1234567890123456789012345678901234567890",
                "name": "Omega Growth Fund",
                "symbol": "OGF",
                "description": "High-growth DeFi assets fund",
                "totalAUM": 1500000,
                "navPerShare": 1.15,
                "totalShares": 1304347,
                "performance": {
                    "daily": 0.5,
                    "weekly": 2.3,
                    "monthly": 8.7,
                    "yearly": 45.2
                },
                "omegaScore": 8500,
                "minInvestment": 10
            },
            {
                "address": "0x2345678901234567890123456789012345678901",
                "name": "Omega Stable Fund",
                "symbol": "OSF",
                "description": "Stable income with low volatility",
                "totalAUM": 3200000,
                "navPerShare": 1.08,
                "totalShares": 2962962,
                "performance": {
                    "daily": 0.1,
                    "weekly": 0.6,
                    "monthly": 2.5,
                    "yearly": 12.3
                },
                "omegaScore": 9200,
                "minInvestment": 10
            }
        ]

        return {
            "funds": funds,
            "total": len(funds)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{fund_address}")
async def get_fund_details(fund_address: str, app_request: Request):
    """
    Get detailed information about a specific fund
    """
    try:
        w3 = app_request.app.state.w3
        web3_service = Web3Service(w3)

        # Get metrics from contract
        metrics = web3_service.get_fund_metrics(fund_address)

        fund_details = {
            "address": fund_address,
            "name": "Omega Growth Fund",
            "symbol": "OGF",
            "description": "High-growth DeFi assets fund",
            "totalAUM": metrics.get("totalAUM", 0),
            "navPerShare": metrics.get("navPerShare", 0),
            "totalShares": metrics.get("totalShares", 0),
            "holdings": [
                {"asset": "ETH", "percentage": 35, "value": 525000},
                {"asset": "BTC", "percentage": 30, "value": 450000},
                {"asset": "MATIC", "percentage": 20, "value": 300000},
                {"asset": "LINK", "percentage": 15, "value": 225000}
            ],
            "performance": {
                "daily": 0.5,
                "weekly": 2.3,
                "monthly": 8.7,
                "yearly": 45.2
            },
            "omegaScore": 8500,
            "riskMetrics": {
                "psi": 85,
                "theta": 92,
                "cvar": 12,
                "pole": 88
            }
        }

        return fund_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invest")
async def invest_in_fund(request: InvestmentRequest, app_request: Request):
    """
    Process investment in a fund
    This would typically be called after LUA-PAY confirmation
    """
    try:
        # In production, this would trigger contract interaction
        return {
            "success": True,
            "fund_address": request.fund_address,
            "amount": request.amount,
            "investor": request.investor_address,
            "message": "Investment processed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{fund_address}/investors/{investor_address}")
async def get_investor_position(
    fund_address: str,
    investor_address: str,
    app_request: Request
):
    """
    Get investor's position in a specific fund
    """
    try:
        # Mock data (in production, fetch from contract)
        position = {
            "fund_address": fund_address,
            "investor_address": investor_address,
            "shares": 1000,
            "currentValue": 1150,
            "investedAmount": 1000,
            "profitLoss": 150,
            "profitLossPercentage": 15.0,
            "investments": [
                {
                    "amount": 500,
                    "timestamp": 1700000000,
                    "invoiceId": "inv_abc123"
                },
                {
                    "amount": 500,
                    "timestamp": 1700100000,
                    "invoiceId": "inv_def456"
                }
            ]
        }

        return position

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{fund_address}/redeem")
async def redeem_shares(
    fund_address: str,
    shares: float,
    investor_address: str,
    app_request: Request
):
    """
    Redeem fund shares
    """
    try:
        # In production, call fund contract to redeem shares
        redemption_value = shares * 1.15  # Mock NAV

        return {
            "success": True,
            "fund_address": fund_address,
            "shares_redeemed": shares,
            "redemption_value": redemption_value,
            "investor": investor_address,
            "message": "Redemption processed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
