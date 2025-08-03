from typing import Annotated, List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db
from domain.models.website_model import WebsitePlan, SubscriptionPlan, Website
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import joinedload
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract
from datetime import datetime, timedelta

class PlanRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def deactivate_expired_plans(self):
        now = datetime.utcnow()
        expired_plans = self.db.query(WebsitePlan).filter(
            WebsitePlan.expires_at <= now,
            WebsitePlan.is_active == True
        ).all()
        for plan in expired_plans:
            plan.is_active = False
        self.db.commit()
        self.db.close()
        return expired_plans

    def get_active_plan_by_website_id(self, website_id: UUID) -> WebsitePlan:
        plan =  (
            self.db.query(WebsitePlan).options(joinedload(WebsitePlan.plan))
            .filter(WebsitePlan.website_id == website_id, WebsitePlan.is_active == True)
            .first()
        )
        return plan

    def get_plan_price(self, name: UUID) -> float:
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == name).first()

        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        return plan.price

    def get_plan_by_id(self, plan_id: UUID) -> SubscriptionPlan:
        return self.db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_id == plan_id).first()


    def deactivate_all_website_plans(self, website_id):
        self.db.query(WebsitePlan)\
                .filter(WebsitePlan.website_id == website_id, WebsitePlan.is_active == True)\
                .update({WebsitePlan.is_active: False})
        self.db.commit()

    def create_website_plan(self, website_id, plan_id, price):
        activated_at=datetime.utcnow()
        expires_at = activated_at + timedelta(days=90)
        website_plan = WebsitePlan(
            website_id=website_id,
            plan_id=plan_id,
            activated_at=activated_at,
            expires_at=expires_at,
            is_active=True
        )
        self.db.add(website_plan)
        self.db.commit()
        self.db.refresh(website_plan)
        return website_plan
    
    def create_free_website_plan(self, website_id, plan_id):
        activated_at=datetime.utcnow()
        expires_at = activated_at + relativedelta(days=7)
        website_plan = WebsitePlan(
            website_id=website_id,
            plan_id=plan_id,
            activated_at=activated_at,
            expires_at=expires_at,
            is_active=True
        )
        self.db.add(website_plan)
        self.db.commit()
        self.db.refresh(website_plan)
        return website_plan


    def get_active_plan_counts(self):
        result = (
            self.db.query(SubscriptionPlan.name, func.count())
            .select_from(WebsitePlan)
            .join(SubscriptionPlan, SubscriptionPlan.plan_id == WebsitePlan.plan_id)
            .filter(WebsitePlan.is_active == True)
            .group_by(SubscriptionPlan.name)
            .all()
    )

        return {name: count for name, count in result}
    

    def get_total_earned_amount(self):
        total = (
            self.db.query(func.sum(SubscriptionPlan.price))
            .select_from(WebsitePlan)
            .join(SubscriptionPlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
            .scalar()
        )

        return total or 0
    


    def get_active_and_inactive_websites(self):
        active_count = self.db.query(func.count()).select_from(WebsitePlan).filter(WebsitePlan.is_active == True).scalar()
        inactive_count = self.db.query(func.count()).select_from(WebsitePlan).filter(WebsitePlan.is_active == False).scalar()

        return {
            "active": active_count,
            "inactive": inactive_count
        }
 

    def get_all_active_websites_with_plans(self) -> list[Website]:
        return (
            self.db.query(Website)
            .join(WebsitePlan, WebsitePlan.website_id == Website.website_id)
            .join(SubscriptionPlan, SubscriptionPlan.plan_id == WebsitePlan.plan_id)
        ).all()



    def get_total_earned_amount(self):
            return (
                self.db.query(func.sum(SubscriptionPlan.price))
                .join(WebsitePlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
                .scalar()
            ) or 0

    def get_earned_amount_by_month(self, start: datetime, end: datetime):
        return (
            self.db.query(func.sum(SubscriptionPlan.price))
            .join(WebsitePlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
            .filter(WebsitePlan.activated_at >= start, WebsitePlan.activated_at < end)
            .scalar()
        ) or 0

    def get_earned_amount_by_year(self, year: int):
        return (
            self.db.query(func.sum(SubscriptionPlan.price))
            .join(WebsitePlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
            .filter(extract("year", WebsitePlan.activated_at) == year)
            .scalar()
        ) or 0
    

    def get_revenue_by_plan_type(self) -> dict:
        result = (
            self.db.query(SubscriptionPlan.name, func.sum(SubscriptionPlan.price))
            .join(WebsitePlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
            .group_by(SubscriptionPlan.name)
            .all()
        )
        return {plan: amount for plan, amount in result}
    

    def get_website_plan_counts(self) -> List[tuple]:
        return (
            self.db.query(
                WebsitePlan.website_id,
                Website.business_name,
                SubscriptionPlan.name,
                func.count(),                   
                (func.count() * SubscriptionPlan.price).label("total_revenue")
            )
            .join(SubscriptionPlan, WebsitePlan.plan_id == SubscriptionPlan.plan_id)
            .join(Website, Website.website_id == WebsitePlan.website_id)
            .group_by(WebsitePlan.website_id, Website.business_name, SubscriptionPlan.name, SubscriptionPlan.price)
            .order_by(func.count().desc())
            .all()
        )

    def get_basic_plan(self):
        return self.db.query(SubscriptionPlan).filter(SubscriptionPlan.name == 'Basic').first()

    def get_all_plans(self):
        plans = self.db.query(SubscriptionPlan).all()
        return [
            {
                "id": p.plan_id,
                "name": p.name,
                "price": p.price
            }
            for p in plans
        ]
    
    def check_had_paln(self, website_id:UUID):
        return self.db.query(WebsitePlan).filter(WebsitePlan.website_id == website_id).first()

    def get_left_days(self, website_id:UUID):
        plan = self.get_active_plan_by_website_id(website_id)
        now = datetime.utcnow()
        expiration_time = plan.expires_at - now 
        return expiration_time.days