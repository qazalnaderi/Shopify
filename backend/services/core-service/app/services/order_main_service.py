from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException
from services.base_service import BaseService
from services.order_service import OrderService
from services.item_service import ItemService
from services.user_service import UserService
from services.buyer_service import BuyerService

from domain.schemas.order_schema import OrderResponseSchema, OrderItemResponseSchema, OrderFactorResponseSchema
from domain.models.order_model import Order
from loguru import logger
from typing import Annotated
from services.coupon_main_service import CouponMainService
class OrderMainService(BaseService):
    def __init__(self,  
        order_service : Annotated[OrderService, Depends()],
        user_service : Annotated[UserService, Depends()],
        buyer_service : Annotated[BuyerService, Depends()],
        item_service : Annotated[ItemService, Depends()],
        coupon_service : Annotated[CouponMainService, Depends()],
        ):
        super().__init__()
        self.order_service = order_service
        self.user_service = user_service
        self.item_service = item_service
        self.coupon_service = coupon_service
        self.buyer_service = buyer_service

    async def create_order(self, buyer_id: UUID, website_id: UUID) -> OrderResponseSchema:
        
        logger.info(f"Creating order for buyer...")
        order = await self.order_service.create_order_from_cart(buyer_id, website_id)
        
        order_items_response = []
        for item in order.order_items:
            item_obj = await self.item_service.get_item_by_id(item.item_id)
            item_name = item_obj.name if item_obj else "null"

            order_items_response.append(OrderItemResponseSchema(
                order_item_id=item.order_item_id,
                item_id=item.item_id,
                item_name=item_name,
                quantity=item.quantity,
                price=item.price,
            ))

        return OrderResponseSchema(
            order_id=order.order_id,
            website_id=order.website_id,
            buyer_id=order.buyer_id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at,
            order_items=order_items_response
        )
    
    async def get_my_orders(self, buyer_id: UUID) -> List[OrderResponseSchema]:
        logger.info("Getting orders for buyer...")
        orders: List[Order] = await self.order_service.get_orders_by_buyer(buyer_id)

        response = []
        for order in orders:
            order_items_response = []
            for item in order.order_items:
                item_obj = await self.item_service.get_item_by_id(item.item_id)
                item_name = item_obj.name if item_obj else "null"

                order_items_response.append(OrderItemResponseSchema(
                    order_item_id=item.order_item_id,
                    item_id=item.item_id,
                    item_name=item_name,
                    quantity=item.quantity,
                    price=item.price,
                ))

            response.append(OrderResponseSchema(
                order_id=order.order_id,
                website_id=order.website_id,
                buyer_id=order.buyer_id,
                status=order.status,
                total_price=order.total_price,
                created_at=order.created_at,
                order_items=order_items_response
            ))

        return response
        
    async def get_order_by_id(self,order_id: UUID) -> OrderResponseSchema:
        
        logger.info(f"Getting order ...")
        order = await self.order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order_items_response = []
        for item in order.order_items:
            item_obj = await self.item_service.get_item_by_id(item.item_id)
            item_name = item_obj.name if item_obj else "null"

            order_items_response.append(OrderItemResponseSchema(
                order_item_id=item.order_item_id,
                item_id=item.item_id,
                item_name=item_name,
                quantity=item.quantity,
                price=item.price,
            ))

        return OrderResponseSchema(
            order_id=order.order_id,
            website_id=order.website_id,
            buyer_id=order.buyer_id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at,
            order_items=order_items_response
        )
        

    async def get_orders_by_website_id(self,website_id: UUID) -> OrderFactorResponseSchema:
        
        logger.info(f"Getting order ...")
        orders: List[Order] = await self.order_service.get_orders_by_website_id(website_id)

        response = []
        for order in orders:
            order_items_response = []
            for item in order.order_items:
                buyer = await self.buyer_service.get_buyer_by_id(order.buyer_id)
                item_obj = await self.item_service.get_item_by_id(item.item_id)
                item_name = item_obj.name if item_obj else "null"
                order_number = f"{order.created_at.strftime('%Y%m%d')}-{buyer.email.split('@')[0]}-{int(order.total_price)}"

                order_items_response.append(OrderItemResponseSchema(
                    order_item_id=item.order_item_id,
                    item_id=item.item_id,
                    item_name=item_name,
                    quantity=item.quantity,
                    price=item.price,
                ))

            response.append(OrderFactorResponseSchema(
                order_number = order_number,
                order_id=order.order_id,
                website_id=order.website_id,
                buyer_id=order.buyer_id,
                buyer_email=buyer.email,
                status=order.status,
                total_price=order.total_price,
                created_at=order.created_at,
                order_items=order_items_response
            ))

        return response


    async def get_all_orders(self, user_id: UUID) -> List[OrderResponseSchema]:

        website = await self.user_service.get_website_for_user(user_id)
        orders = await self.get_orders_by_website_id(website.website_id)

        response = []
        for order in orders:
            order_items_response = []
            for item in order.order_items:
                item_obj = await self.item_service.get_item_by_id(item.item_id)
                item_name = item_obj.name if item_obj else "null"

                order_items_response.append(OrderItemResponseSchema(
                    order_item_id=item.order_item_id,
                    item_id=item.item_id,
                    item_name=item_name,
                    quantity=item.quantity,
                    price=item.price,
                ))

            response.append(OrderResponseSchema(
                order_id=order.order_id,
                website_id=order.website_id,
                buyer_id=order.buyer_id,
                status=order.status,
                total_price=order.total_price,
                created_at=order.created_at,
                order_items=order_items_response
            ))

        return response
    


    async def get_pending_order(self, buyer_id: UUID) -> List[OrderResponseSchema]:
        logger.info("Getting pending orders for buyer...")
        order = await self.order_service.get_pending_order(buyer_id)
        order_items_response = []
        for item in order.order_items:
            item_obj = await self.item_service.get_item_by_id(item.item_id)
            item_name = item_obj.name if item_obj else "null"

            order_items_response.append(OrderItemResponseSchema(
                order_item_id=item.order_item_id,
                item_id=item.item_id,
                item_name=item_name,
                quantity=item.quantity,
                price=item.price,
            ))

        return OrderResponseSchema(
            order_id=order.order_id,
            website_id=order.website_id,
            buyer_id=order.buyer_id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at,
            order_items=order_items_response
        )
    
    

    async def get_item_delivery_url(self, buyer_id: UUID, item_id: UUID) -> str:
        logger.info("Getting url...")
        order_item = await self.order_service.get_order_item_by_buyer_and_item(buyer_id, item_id)
        
        if not order_item:
            raise HTTPException(status_code=403, detail="You should buy this item first.")
        

        logger.info("We are here")
        
        item = await self.item_service.get_item_by_id(item_id)
        return item.delivery_url
    
    async def get_sales_count(self, item_id: UUID) -> int:
        return await self.order_service.get_sales_count(item_id)
    
    async def get_item_revenue(self, item_id: UUID) -> int:
        return await self.order_service.get_item_revenue(item_id)

    async def apply_coupon_to_order(self,order_id: UUID, coupon_code: str)-> OrderResponseSchema:
        order = await self.order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        coupon = await self.coupon_service.get_coupon_by_code(coupon_code)
        if not coupon:
            raise HTTPException(status_code=404, detail="Coupon not found")


        updated_order = await self.order_service.apply_coupon_to_order(order, coupon)

        order_items_response = []
        for item in updated_order.order_items:
            item_obj = await self.item_service.get_item_by_id(item.item_id)
            item_name = item_obj.name if item_obj else "null"

            order_items_response.append(OrderItemResponseSchema(
                order_item_id=item.order_item_id,
                item_id=item.item_id,
                item_name=item_name,
                quantity=item.quantity,
                price=item.price,
            ))

        return OrderResponseSchema(
            order_id=updated_order.order_id,
            website_id=updated_order.website_id,
            buyer_id=updated_order.buyer_id,
            status=updated_order.status,
            total_price=updated_order.total_price,
            created_at=updated_order.created_at,
            order_items=order_items_response
        )
    
