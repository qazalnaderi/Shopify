from typing import Annotated
from services.payment_main_service import PaymentMainService
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from services.auth_services.user_auth_service import  get_current_user
from services.auth_services.buyer_auth_service import get_current_buyer

from domain.schemas.token_schema import TokenDataSchema
from loguru import logger
from fastapi.responses import RedirectResponse, JSONResponse

payment_router = APIRouter()

@payment_router.post("/order_request")
async def request_order_payment(
    website_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    payment_main_service: Annotated[PaymentMainService, Depends()] ,
):
    logger.info(f"Buyer {current_buyer.buyer_id} is starting to pay...")
    payment_url = await payment_main_service.initiate_order_payment(website_id, current_buyer.buyer_id)
    return {"payment_url": payment_url}


@payment_router.get("/order_payment/callback/{order_id}")
async def payment_callback(
    payment_main_service: Annotated[PaymentMainService, Depends()],
    order_id: UUID,
    authority: str = Query(..., alias="Authority"),  
    status: str = Query(..., alias="Status"),
    website_id: UUID = Query(..., alias="website_id")    
):
    result = await payment_main_service.confirm_order_payment(order_id, authority, status)
    frontend_url = (
        f"http://localhost:5173/website/orders/payment-callback"
        f"?orderId={order_id}&authority={authority}&status={status}&websiteId={website_id}"
    ) 
    return RedirectResponse(url=frontend_url)

@payment_router.post("/plan_payment_request/{plan_id}")
async def request_plan_payment(
    plan_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    payment_main_service: Annotated[PaymentMainService, Depends()],
):
    logger.info(f"user {current_user.user_id} is starting plan payment for plan {plan_id}...")
    payment_url = await payment_main_service.initiate_plan_payment(current_user.user_id, plan_id)
    return {"payment_url": payment_url}



@payment_router.get("/plan_payment/callback")
async def plan_payment_callback(
    payment_main_service: Annotated[PaymentMainService, Depends()],
    website_id: UUID = Query(...),
    plan_id: UUID = Query(...),
    authority: str = Query(..., alias="Authority"),
    status: str = Query(..., alias="Status"),

):
    result = await payment_main_service.confirm_plan_payment(website_id, plan_id, authority, status)
    frontend_url = f"http://localhost:5173/payment/callback?status={result}"
    return RedirectResponse(url=frontend_url)