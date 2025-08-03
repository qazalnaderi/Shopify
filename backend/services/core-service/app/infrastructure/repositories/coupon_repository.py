from sqlalchemy.orm import Session
from domain.models.website_model import Coupon
from core.postgres_db.database import get_db
from fastapi import Depends
from typing import Annotated, Optional, List
from uuid import UUID

class CouponRepository:
    def __init__(self,db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create_coupon(self, coupon: Coupon) -> Coupon:
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon
    

    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        return self.db.query(Coupon).filter_by(code=code).first()
    
    def get_coupons_by_website_id(self, website_id: UUID) -> List[Coupon]:
        return self.db.query(Coupon).filter_by(website_id=website_id).all()
    
    def update_coupon(self, coupon: Coupon) -> Coupon:
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon
    
    def increment_times_used(self, coupon_id: UUID):
        self.db.query(Coupon).filter(Coupon.coupon_id == coupon_id).update({
            Coupon.times_used: Coupon.times_used + 1
        })
        self.db.commit()

    def get_coupon_by_id(self, coupon_id: UUID) -> Optional[Coupon]:
        return self.db.query(Coupon).filter_by(coupon_id=coupon_id).first()

    def delete_coupon(self, coupon_id: UUID) -> None:
        coupon = self.get_coupon_by_id(coupon_id)
        if coupon:
            self.db.delete(coupon)
            self.db.commit()
