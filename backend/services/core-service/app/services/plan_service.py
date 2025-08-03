from infrastructure.repositories.plan_repository import PlanRepository
from infrastructure.repositories.item_repository import ItemRepository
from domain.models.website_model import WebsitePlan, Website
from uuid import UUID
from fastapi import HTTPException, Depends
from infrastructure.repositories.website_repository import WebsiteRepository
from typing import Annotated, List
from loguru import logger
from datetime import datetime
from decimal import Decimal



class PlanService:
    def __init__(
        self,
        plan_repository: Annotated[PlanRepository, Depends()],
        item_repository: Annotated[ItemRepository, Depends()],
        website_repository: Annotated[WebsiteRepository, Depends()],

    ) -> None:
        self.plan_repository = plan_repository
        self.item_repository = item_repository
        self.website_repository = website_repository



    async def get_active_plan_by_website_id(self, website_id: UUID) -> WebsitePlan:
        logger.info(f"Fetching active plan for website ID: {website_id}")
        return self.plan_repository.get_active_plan_by_website_id(website_id)
    
        
    async def check_item_limit(self, website_id: UUID):
        active_plan = await self.get_active_plan_by_website_id(website_id)

        if not active_plan:
            raise HTTPException(status_code=403, detail="No active plan for this website.")
        logger.info(f"Active plan for website ID: {website_id} is {active_plan}")


        item_count = self.item_repository.count_items_by_website_id(website_id)

        if item_count >= active_plan.plan.item_limit:
            raise HTTPException(status_code=403, detail="Item limit exceeded for this plan.")
        

    async def check_discount_permission(self, website_id: UUID) -> bool:
        active_plan = self.plan_repository.get_active_plan_by_website_id(website_id)
        if not active_plan:
            raise HTTPException(status_code=403, detail="No active plan for this website.")
        if not active_plan.plan.allow_discount :
            raise HTTPException(status_code=403, detail="Your plan does not allow discount features.")
    

    async def get_plan_by_id(self, plan_id: UUID):
        plan = self.plan_repository.get_plan_by_id(plan_id)
        if not plan:
            raise  HTTPException(status_code=404, detail="Plan not found")
        return plan



    async def activate_plan_for_website(self, website_id, plan_id, price):
            self.plan_repository.deactivate_all_website_plans(website_id)
            self.plan_repository.create_website_plan(
                website_id=website_id,
                plan_id=plan_id,
                price=price,
            )
            return True
    

    async def get_all_websites(self) -> list[Website]:
        return self.plan_repository.get_all_active_websites_with_plans()
    
    async def get_total_earned_amount(self) -> Decimal:
        return self.plan_repository.get_total_earned_amount()

    async def get_earned_amount_by_month(self, start: datetime, end: datetime) -> Decimal:
        return self.plan_repository.get_earned_amount_by_month(start, end)

    async def get_earned_amount_by_year(self, year: int) -> Decimal:
        return self.plan_repository.get_earned_amount_by_year(year)


    async def get_revenue_by_plan_type(self) -> dict:
        return self.plan_repository.get_revenue_by_plan_type()

    async def get_plan_purchase_stats(self) -> List[dict]:
        return self.plan_repository.get_website_plan_counts()
    

    async def get_all_plans(self):
        return self.plan_repository.get_all_plans()
    

    async def activate_free_plan(self, website_id:UUID):
        website = self.website_repository.get_website_by_id(website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found.")
        # active_plan = self.get_active_plan_by_website_id(website_id)
        # if active_plan:
        #     raise HTTPException(status_code=400, detail="This website already has an active plan.")
        basic_plan = self.plan_repository.get_basic_plan()
        self.plan_repository.create_free_website_plan(website_id, basic_plan.plan_id)


    async def check_had_plan(self, website_id:UUID): 
        return self.plan_repository.check_had_paln(website_id)  
        
        
    async def get_left_days(self,website_id:UUID):
        return self.plan_repository.get_left_days(website_id)    
    
    