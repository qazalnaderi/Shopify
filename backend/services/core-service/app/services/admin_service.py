from typing import Annotated, Dict
from loguru import logger
from domain.models.admin_model import Admin
from infrastructure.repositories.admin_repository import AdminRepository
from domain.schemas.admin_schema import ShopPlanStatsSchema, TopWebsiteSchema
from services.base_service import BaseService
from uuid import UUID
from infrastructure.repositories.plan_repository import PlanRepository
from infrastructure.repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException
from datetime import datetime
from decimal import Decimal

class AdminService(BaseService):
    def __init__(
        self,
        admin_repository: Annotated[AdminRepository, Depends()],
        plan_repository: Annotated[PlanRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        super().__init__()
        self.admin_repository = admin_repository
        self.plan_repository = plan_repository
        self.user_repository = user_repository

    async def get_admin_by_email(self, email: str) -> Admin:
        logger.info(f"📥 Fetching admin with email {email}")
        return self.admin_repository.get_admin_by_email(email)

    async def get_admin_by_id(self, admin_id: UUID) -> Admin:  
        logger.info(f"📥 Fetching admin with id {admin_id}")
        return self.admin_repository.get_admin_by_id(admin_id) 

    async def get_dashboard_shop_stats(self) -> ShopPlanStatsSchema:
        counts = self.plan_repository.get_active_plan_counts()
        return ShopPlanStatsSchema(
        total_active=sum(counts.values()),
        basic_active=counts.get("basic", counts.get("Basic", 0)),
        pro_active=counts.get("pro", counts.get("Pro", 0)),
    ) 

    async def get_user_and_seller_stats(self):
        return self.user_repository.get_user_and_seller_counts()
    
    async def get_total_revenue(self) -> int:
        return self.plan_repository.get_total_earned_amount()
    
    async def get_website_activity_stats(self):
        return self.plan_repository.get_active_and_inactive_websites()
