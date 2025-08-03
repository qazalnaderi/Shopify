from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from uuid import UUID
from domain.schemas.order_schema import OrderCreateSchema, OrderResponseSchema, OrderFactorResponseSchema
from domain.schemas.token_schema import TokenDataSchema
from services.order_main_service import OrderMainService
from services.auth_services.buyer_auth_service import get_current_buyer
from services.auth_services.user_auth_service import  get_current_user

from loguru import logger

order_router = APIRouter()

@order_router.post("/create_order", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    website_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    if current_buyer.website_id != website_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this website.")
    
    logger.info(f"Buyer {current_buyer.buyer_id} creating order for website {website_id}")
    return await order_main_service.create_order(current_buyer.buyer_id, website_id)


@order_router.get("/my_orders", response_model=List[OrderResponseSchema], status_code=status.HTTP_200_OK)
async def get_my_orders(
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    return await order_main_service.get_my_orders(current_buyer.buyer_id)


@order_router.get("/order/{order_id}", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def get_order_by_id(
    order_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    
    logger.info(f"Fetching order with ID: {order_id}")
    order_response = await order_main_service.get_order_by_id(order_id)
    return order_response


@order_router.get("/orders/invoice-table/{order_id}", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def get_order_by_id(
    order_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    
    logger.info(f"Fetching order with ID: {order_id}")
    order_response = await order_main_service.get_order_by_id(order_id)
    return order_response


@order_router.get("/orders/{website_id}", response_model=List[OrderFactorResponseSchema], status_code=status.HTTP_201_CREATED)
async def get_orders_by_website_id(
    website_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    
    logger.info(f"Fetching order with ID: {website_id}")
    return await order_main_service.get_orders_by_website_id(website_id)


@order_router.get("/download_link/{item_id}", status_code=status.HTTP_200_OK)
async def get_download_link(
    item_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    order_main_service: Annotated[OrderMainService, Depends()],
):
    url = await order_main_service.get_item_delivery_url(current_buyer.buyer_id, item_id)
    
    return {"download_link": url}


@order_router.get("/items/{item_id}/sales")
async def get_item_sales(
    item_id: UUID,
    order_main_service: Annotated[OrderMainService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
):
    total = await order_main_service.get_sales_count(item_id)
    return {"total_sold": total}

@order_router.get("/items/{item_id}/revenue")
async def get_item_revenue(
    item_id: UUID,
    order_main_service: Annotated[OrderMainService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
):
    revenue = await order_main_service.get_item_revenue(item_id)
    return {"revenue": revenue}


@order_router.post("/apply_coupon", response_model=OrderResponseSchema)
async def apply_coupon(
    order_id: UUID,
    coupon_code: str,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    order_main_service: Annotated[OrderMainService, Depends()]
):
    return await order_main_service.apply_coupon_to_order(order_id, coupon_code)
