from services.plan_service import PlanService
from uuid import UUID
from fastapi import Depends
from services.base_service import BaseService
from typing import Annotated

class PlanMainService(BaseService):
    def __init__(
        self,
        service: Annotated[PlanService, Depends()],
    ) -> None:
        super().__init__()
        self.service = service


    async def get_all_plans(self):
        return await self.service.get_all_plans()
    

    async def activate_free_plan(self, website_id:UUID):
        return await self.service.activate_free_plan(website_id)


    async def check_had_plan(self, website_id:UUID): 
        plan = self.service.check_had_plan(website_id)
        if plan:
            return True
        else:
            return False
        
    async def get_left_days(self,website_id:UUID):
        return self.service.get_left_days(website_id)        