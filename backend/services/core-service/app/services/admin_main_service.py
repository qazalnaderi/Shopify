
from services.admin_service import AdminService
from services.plan_service import PlanService
from services.website_service import WebsiteService
from domain.schemas.admin_schema import ShopPlanStatsSchema, TopWebsiteSchema, WebsiteListSchema 
from typing import Annotated, List
from fastapi import Depends
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.date_utils import get_jalali_month_year

class AdminMainService:
    def __init__(self,
                 admin_service: Annotated[AdminService, Depends()],
                 website_service: Annotated[WebsiteService, Depends()],
                 plan_service: Annotated[PlanService, Depends()],):
        self.admin_service = admin_service
        self.plan_service = plan_service
        self.website_service = website_service

    async def get_shop_plan_stats(self) -> ShopPlanStatsSchema:
        return await self.admin_service.get_dashboard_shop_stats()
    

    async def get_user_and_seller_stats(self):
        return await self.admin_service.get_user_and_seller_stats()
    
    async def get_total_revenue(self) -> int:
        return await self.admin_service.get_total_revenue()
    
    async def get_website_activity_stats(self):
        return await self.admin_service.get_website_activity_stats()

    async def get_top_websites(self, sort_by: str , limit: int ) -> list[TopWebsiteSchema]:
        websites = await self.plan_service.get_all_websites() 
        result = []

        for site in websites:
            income_data = await self.website_service.get_total_revenue(site.website_id)
            total_income = income_data.get("total_revenue", 0)

            sales_count = await self.website_service.get_total_sales_count(site.website_id)
            owner_email = await self.website_service.get_website_owner_email(site.website_id)
            website_plan = await self.plan_service.get_active_plan_by_website_id(site.website_id)
            plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)

            result.append(TopWebsiteSchema(
                website_id=str(site.website_id),
                website_name=site.business_name,
                is_active = website_plan.is_active if website_plan else False,
                owner_email=owner_email,  
                plan_name = plan.name if plan else "Inactive",
                total_income=total_income,
                total_orders=sales_count
            ))

        if sort_by == "income":
            result.sort(key=lambda website: website.total_income, reverse=True)
        elif sort_by == "sales":
            result.sort(key=lambda website: website.total_orders, reverse=True)

        top_websites = result[:limit]
        return top_websites
    


    async def get_website_table(self, sort_by: str) -> list[WebsiteListSchema]:
            websites = await self.website_service.get_all_websites()   

            result = []
            for site in websites:
                income_data = await self.website_service.get_total_revenue(site.website_id)
                total_income = income_data.get("total_revenue", 0)

                owner_emails = await self.website_service.get_website_owner_email(site.website_id)
                website_plan = await self.plan_service.get_active_plan_by_website_id(site.website_id)

                if website_plan:
                    plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
                    plan_name = plan.name if plan else "Unknown"
                    is_plan_active = website_plan.is_active
                else:
                    plan_name = "Inactive"
                    is_plan_active = False


                result.append(WebsiteListSchema(
                    website_id=site.website_id,
                    website_name=site.business_name,
                    is_active=is_plan_active,
                    created_at=site.created_at,
                    owner_emails=owner_emails,
                    plan_name=plan_name,
                    total_income=total_income or 0
                ))

            if sort_by == "revenue":
                result.sort(key=lambda x: x.total_income, reverse=True)
            else:
                result.sort(key=lambda x: x.created_at, reverse=True)

            return result
    

    async def get_revenue_stats(self) -> dict:
        now = datetime.utcnow()
        start_of_month = now.replace(day=1)
        start_of_prev_month = (start_of_month - timedelta(days=1)).replace(day=1)
        start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

        this_year = now.year
        last_year = this_year - 1

        total = await self.plan_service.get_total_earned_amount()
        monthly = await self.plan_service.get_earned_amount_by_month(start_of_month, start_of_next_month)
        prev_month = await self.plan_service.get_earned_amount_by_month(start_of_prev_month, start_of_month)
        this_year_total = await self.plan_service.get_earned_amount_by_year(this_year)
        last_year_total = await self.plan_service.get_earned_amount_by_year(last_year)

        monthly_growth = ((monthly - prev_month) / prev_month * 100) if prev_month else 0
        yearly_growth = ((this_year_total - last_year_total) / last_year_total * 100) if last_year_total else 0

        return {
            "total_revenue": total,
            "monthly_revenue": monthly,
            "monthly_growth": round(monthly_growth),
            "yearly_revenue": this_year_total,
            "yearly_growth": round(yearly_growth)
        }
    

    async def get_last_6_months_revenue_trend(self):
        now = datetime.utcnow().replace(day=1)
        months = [(now - relativedelta(months=i)) for i in reversed(range(6))]

        result = {"labels": [], "values": []}

        for m in months:
            start = m
            end = (m + relativedelta(months=1))

            revenue = await self.plan_service.get_earned_amount_by_month(start, end)
            label = get_jalali_month_year(start)

            result["labels"].append(label)
            result["values"].append(revenue or 0)

        return result
    

    async def get_plan_revenue_breakdown(self) -> dict:
        return await self.plan_service.get_revenue_by_plan_type()
    

    async def get_plan_purchase_stats(self) -> List[dict]:
        raw_data = await self.plan_service.get_plan_purchase_stats()
        result = []

        for row in raw_data:
            website_id = row[0]
            website_name = row[1]
            plan_type = row[2]
            plan_count = row[3]
            total_revenue = row[4]

            result.append({
                "website_id": website_id,
                "website_name": website_name,
                "plan_type": plan_type,
                "plan_count": plan_count,
                "total_revenue": total_revenue
            })

        return result


    async def get_monthly_revenue_growth(self) -> float:
        now = datetime.utcnow()
        start_of_month = now.replace(day=1)
        start_of_prev_month = (start_of_month - timedelta(days=1)).replace(day=1)
        start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

        current_month_income = await self.plan_service.get_earned_amount_by_month(start_of_month, start_of_next_month)
        last_month_income = await self.plan_service.get_earned_amount_by_month(start_of_prev_month, start_of_month)

        if not last_month_income:
            return 0.0

        growth = ((current_month_income - last_month_income) / last_month_income) * 100
        return round(growth, 2)