from fastapi import APIRouter, Depends, HTTPException, status
from services.cart_main_service import CartMainService
from domain.schemas.cart_schema import CartItemCreateSchema, CartItemResponseSchema, MessageResponse
from typing import Annotated, List
from uuid import UUID
from services.auth_services.buyer_auth_service import get_current_buyer
from domain.schemas.token_schema import TokenDataSchema
from loguru import logger

cart_router = APIRouter()

@cart_router.post("/add_item", response_model=CartItemResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_data: CartItemCreateSchema,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    cart_main_service: Annotated[CartMainService, Depends()]
):
    logger.info(f"Buyer {current_buyer.buyer_id} adding item {cart_data.item_id} to cart")
    return await cart_main_service.add_item(
        cart_data.website_id,
        current_buyer.buyer_id,
        cart_data.item_id,
    )


@cart_router.get("/my_cart", response_model=List[CartItemResponseSchema], status_code=status.HTTP_200_OK)
async def get_my_cart(
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    cart_main_service: Annotated[CartMainService, Depends()]
):
    logger.info(f"buyer {current_buyer.buyer_id} fetching their cart items")
    return await cart_main_service.get_cart_items(current_buyer.buyer_id)


@cart_router.post(
    "/remove_one_from_cart/{cart_item_id}",
    status_code=status.HTTP_200_OK,
)
async def remove_one_from_cart(
    cart_item_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    cart_main_service: Annotated[CartMainService, Depends()],
):
    logger.info(f"Buyer {current_buyer.buyer_id} removing item {cart_item_id} to cart")
    
    message = await cart_main_service.remove_one_from_cart(cart_item_id)
    return message


@cart_router.delete("/cart/delete_item/{cart_item_id}", response_model=MessageResponse)
async def delete_item_from_cart(
    cart_item_id: UUID,
    current_buyer: Annotated[TokenDataSchema, Depends(get_current_buyer)],
    cart_main_service: Annotated[CartMainService, Depends()]
):
    logger.info(f"Buyer {current_buyer.buyer_id} deleting cart item {cart_item_id}")
    return await cart_main_service.delete_item(cart_item_id)