"""
Payment Routes - LUA-PAY integration endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

from services.lua_pay_service import LUAPayService
from services.web3_service import Web3Service

router = APIRouter()

# Initialize LUA-PAY service
lua_pay_api_key = os.getenv("LUA_PAY_API_KEY", "demo_key")
lua_pay_secret = os.getenv("LUA_PAY_SECRET", "demo_secret")
lua_service = LUAPayService(lua_pay_api_key, lua_pay_secret)


class CreateInvoiceRequest(BaseModel):
    amount: float
    currency: str = "USDT"
    description: str = "Omega Capitals Investment"
    product_type: str = "OmegaFund"
    user_address: Optional[str] = None


class WebhookPayload(BaseModel):
    invoice_id: str
    status: str
    amount: float
    currency: str
    payer_address: str
    timestamp: str
    metadata: Dict[str, Any] = {}


@router.post("/create-invoice")
async def create_invoice(request: CreateInvoiceRequest, app_request: Request):
    """
    Create a new LUA-PAY invoice for investment
    """
    try:
        metadata = {
            "product_type": request.product_type,
            "user_address": request.user_address
        }

        invoice = lua_service.create_invoice(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            metadata=metadata
        )

        if "error" in invoice:
            raise HTTPException(status_code=500, detail=invoice["error"])

        # Cache invoice in Redis for quick lookup
        redis_client = app_request.app.state.redis
        redis_client.setex(
            f"invoice:{invoice['id']}",
            3600,  # 1 hour expiry
            str(invoice)
        )

        return {
            "invoice_id": invoice.get('id'),
            "amount": request.amount,
            "currency": request.currency,
            "payment_url": invoice.get('pay_url'),
            "qr_code_url": invoice.get('qr_url'),
            "expires_at": invoice.get('expires_at')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/{invoice_id}")
async def verify_payment(invoice_id: str, app_request: Request):
    """
    Verify payment status for an invoice
    """
    try:
        result = lua_service.verify_payment(invoice_id)

        # Update cache
        redis_client = app_request.app.state.redis
        redis_client.setex(
            f"payment_status:{invoice_id}",
            300,  # 5 minutes
            result.get('status', 'unknown')
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def lua_webhook(
    payload: WebhookPayload,
    app_request: Request,
    x_lua_signature: Optional[str] = Header(None)
):
    """
    LUA-PAY webhook endpoint for payment confirmations
    """
    try:
        # Verify webhook signature
        if x_lua_signature:
            is_valid = lua_service.verify_webhook_signature(
                payload.dict(),
                x_lua_signature
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Only process confirmed payments
        if payload.status != "confirmed":
            return {"status": "acknowledged", "message": "Payment not confirmed yet"}

        # Initialize Web3 service
        w3 = app_request.app.state.w3
        web3_service = Web3Service(w3)

        # Process payment and mint NFT
        result = lua_service.process_payment_confirmation(
            invoice_data=payload.dict(),
            web3_service=web3_service
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))

        # Store in Redis for frontend polling
        redis_client = app_request.app.state.redis
        redis_client.setex(
            f"payment_confirmed:{payload.invoice_id}",
            3600,
            str(result)
        )

        return {
            "status": "processed",
            "invoice_id": payload.invoice_id,
            "tx_hash": result.get('tx_hash'),
            "evidence_hash": result.get('evidence_hash')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_payment_stats(start_date: str, end_date: str):
    """
    Get payment statistics for date range
    """
    try:
        stats = lua_service.get_payment_stats(start_date, end_date)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoice/{invoice_id}/status")
async def get_invoice_status(invoice_id: str, app_request: Request):
    """
    Get cached invoice status (faster than API call)
    """
    try:
        redis_client = app_request.app.state.redis

        # Check if payment is confirmed
        confirmed_data = redis_client.get(f"payment_confirmed:{invoice_id}")
        if confirmed_data:
            return {
                "invoice_id": invoice_id,
                "status": "confirmed",
                "data": confirmed_data
            }

        # Check cached status
        status = redis_client.get(f"payment_status:{invoice_id}")
        if status:
            return {
                "invoice_id": invoice_id,
                "status": status,
                "cached": True
            }

        # Fallback to API call
        result = lua_service.verify_payment(invoice_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
