from services.payment_service import PaymentService
from services.order_service import OrderService
from services.user_service import UserService
from services.plan_service import PlanService
from loguru import logger
from fastapi import  Depends, HTTPException
from typing import Annotated
from uuid import UUID

class PaymentMainService:
    def __init__(self, payment_service: Annotated[PaymentService, Depends()],
        order_service: Annotated[OrderService, Depends()],
        plan_service: Annotated[PlanService, Depends()],
        user_service: Annotated[UserService, Depends()]
        ):
        self.payment_service = payment_service 
        self.order_service = order_service 
        self.user_service = user_service
        self.plan_service = plan_service

    async def initiate_order_payment(self, website_id: UUID, buyer_id: UUID) -> str:
        logger.info(f"Initiating payment for buyer: {buyer_id}")
        order = await self.order_service.get_pending_order(website_id, buyer_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        
        payment_url = await self.payment_service.request_order_payment(website_id, order.order_id, amount = order.total_price)
        return payment_url

    async def confirm_order_payment(self, order_id: UUID, authority: str, status: str) -> bool:
        order = await self.order_service.get_order_by_id(order_id)
        if status != "OK":
            await self.order_service.update_order_status(order_id, "Canceled")
            return "Canceled"

        is_successful = await self.payment_service.verify_order_payment(
            amount=float(order.total_price),  
            authority=authority 
        )

        if is_successful:
            await self.order_service.update_order_status(order_id, "Paid")
            await self.order_service.reduce_stock(order_id)
            return "success"
        else:
            await self.order_service.update_order_status(order_id, "Canceled")
            return "failed"
        


    async def initiate_plan_payment(self, user_id: UUID, plan_id: UUID) -> str:
        logger.info(f"Initiating plan payment for website: {user_id}, plan: {plan_id}")
        website = await self.user_service.get_website_for_user(user_id)
        plan = await self.plan_service.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        payment_url = await self.payment_service.request_plan_payment(website.website_id, plan_id, plan.price)
        return payment_url



    async def confirm_plan_payment(self, website_id: UUID, plan_id: UUID, authority: str, status: str) -> str:
        if status != "OK":
            return "Canceled"
        
        plan = await self.plan_service.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        is_successful = await self.payment_service.verify_plan_payment(
            amount=float(plan.price),
            authority=authority
        )
        
        if is_successful:
            await self.plan_service.activate_plan_for_website(
                website_id=website_id,
                plan_id=plan_id,
                price=plan.price
            )
            return "success"
        else:
            return "failed"
