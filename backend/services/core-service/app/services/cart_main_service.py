from services.base_service import BaseService
from services.cart_service import CartService
from services.item_service import ItemService
from typing import Annotated, List, Optional
from fastapi import Depends
from uuid import UUID
from domain.schemas.cart_schema import CartItemResponseSchema, MessageResponse
from loguru import logger

class CartMainService(BaseService):
    def __init__(
            
        self,
        cart_service: Annotated[CartService, Depends()],
        item_service: Annotated[ItemService, Depends()],):
        super().__init__()
        self.cart_service = cart_service
        self.item_service = item_service

        
    async def add_item(self, website_id: UUID, buyer_id: UUID, item_id: UUID) -> CartItemResponseSchema:

        cart_item = await self.cart_service.add_item_to_cart(website_id, buyer_id, item_id)

        item = await self.item_service.get_item_by_id(cart_item.item_id)
        price_per_unit = self.cart_service.calculate_price(item, 1)
        total_price = self.cart_service.calculate_price(item, cart_item.quantity)  
        logger.info(f"Cart item added: {cart_item.id}")

        return CartItemResponseSchema(
        id= cart_item.id, 
        website_id= cart_item.website_id, 
        item_id= cart_item.item_id, 
        item_name= item.name,
        quantity= cart_item.quantity, 
        added_at= cart_item.added_at,
        expires_at= cart_item.expires_at,
        price=item.price,
        discount_price= item.discount_price,
        total_price=total_price,

        )


    async def get_cart_items(self, buyer_id: UUID) -> List[CartItemResponseSchema]:
        logger.info(f"Getting cart for buyer: {buyer_id}")
        cart_items = await self.cart_service.get_cart_items(buyer_id)
        response = []

        for cart_item in cart_items:
            item = await self.item_service.get_item_by_id(cart_item.item_id)
            # price_per_unit = self.cart_service.calculate_price(item, 1)   
            total_price = self.cart_service.calculate_price(item, cart_item.quantity)  

            response.append(
            
            CartItemResponseSchema(
                id=cart_item.id,
                website_id=cart_item.website_id,
                item_id=cart_item.item_id,
                item_name=item.name,
                quantity=cart_item.quantity,
                added_at=cart_item.added_at,
                expires_at=cart_item.expires_at,
                price=item.price,
                discount_price= item.discount_price,
                total_price=total_price,
            )
        )
        return response

    async def remove_one_from_cart(self, cart_item_id: UUID) -> dict:
        updated_item = await self.cart_service.remove_one_from_cart(cart_item_id)
        if updated_item is None:
            return {"message": "Item removed from cart."}
        else:
            return {"message": "Item quantity decreased by one."}
        
    async def delete_item(self, cart_item_id: UUID) -> MessageResponse:
        await self.cart_service.delete_cart_item(cart_item_id)
        return MessageResponse(message="Item deleted from cart.")