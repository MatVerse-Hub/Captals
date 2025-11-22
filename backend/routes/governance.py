"""
Governance Routes - Proposal and voting endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import os

from services.web3_service import Web3Service

router = APIRouter()


class CreateProposalRequest(BaseModel):
    title: str
    description: str
    proposer_address: str


@router.get("/proposals")
async def get_proposals(app_request: Request, skip: int = 0, limit: int = 10):
    """
    Get list of governance proposals
    """
    try:
        redis_client = app_request.app.state.redis

        # Check cache first
        cached_proposals = redis_client.get("proposals:list")
        if cached_proposals:
            # In production, parse and paginate cached data
            pass

        # Mock data for demo (in production, fetch from contract)
        proposals = [
            {
                "id": 1,
                "title": "Update Omega Score Parameters",
                "description": "Proposal to adjust Psi and Theta weights in Omega Score calculation",
                "proposer": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "status": "active",
                "forVotes": 15000,
                "againstVotes": 3000,
                "startTime": 1700000000,
                "endTime": 1700259200
            },
            {
                "id": 2,
                "title": "Add New Asset to Whitelist",
                "description": "Proposal to whitelist LINK token for Omega Funds",
                "proposer": "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                "status": "active",
                "forVotes": 8500,
                "againstVotes": 1200,
                "startTime": 1700100000,
                "endTime": 1700359200
            }
        ]

        # Cache for 5 minutes
        # redis_client.setex("proposals:list", 300, str(proposals))

        return {
            "proposals": proposals[skip:skip + limit],
            "total": len(proposals),
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: int, app_request: Request):
    """
    Get detailed information about a specific proposal
    """
    try:
        # In production, fetch from governance contract
        proposal = {
            "id": proposal_id,
            "title": "Update Omega Score Parameters",
            "description": "Detailed proposal to adjust the Omega Score calculation formula...",
            "proposer": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "status": "active",
            "forVotes": 15000,
            "againstVotes": 3000,
            "startTime": 1700000000,
            "endTime": 1700259200,
            "quorum": 4,
            "votingPower": {
                "total": 100000,
                "voted": 18000
            }
        }

        return proposal

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals")
async def create_proposal(request: CreateProposalRequest, app_request: Request):
    """
    Create a new governance proposal
    """
    try:
        w3 = app_request.app.state.w3
        web3_service = Web3Service(w3)

        # In production, call governance contract to create proposal
        # For now, return mock response

        proposal_id = 3  # Would be returned from contract

        return {
            "success": True,
            "proposal_id": proposal_id,
            "title": request.title,
            "status": "pending",
            "message": "Proposal created successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals/{proposal_id}/vote")
async def vote_on_proposal(
    proposal_id: int,
    voter_address: str,
    support: bool,
    app_request: Request
):
    """
    Cast a vote on a proposal
    """
    try:
        # In production, call governance contract to cast vote
        return {
            "success": True,
            "proposal_id": proposal_id,
            "voter": voter_address,
            "support": support,
            "message": "Vote cast successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}/votes")
async def get_proposal_votes(proposal_id: int, app_request: Request):
    """
    Get all votes for a proposal
    """
    try:
        # Mock data
        votes = [
            {
                "voter": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "support": True,
                "votes": 5000,
                "timestamp": 1700010000
            },
            {
                "voter": "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                "support": True,
                "votes": 10000,
                "timestamp": 1700020000
            },
            {
                "voter": "0xdD2FD4581271e230360230F9337D5c0430Bf44C0",
                "support": False,
                "votes": 3000,
                "timestamp": 1700030000
            }
        ]

        return {
            "proposal_id": proposal_id,
            "votes": votes,
            "total_votes": sum(v["votes"] for v in votes)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
