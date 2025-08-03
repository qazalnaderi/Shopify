from fastapi import HTTPException, Depends
from domain.schemas.coupon_schema import CouponCreateSchema
from domain.models.website_model import Coupon
from infrastructure.repositories.coupon_repository import CouponRepository
from uuid import UUID
from infrastructure.repositories.website_repository import WebsiteRepository
from typing import Annotated, List
from loguru import logger


class CouponService:
    def __init__(
        self,
        coupon_repository: Annotated[CouponRepository, Depends()],
        website_repository: Annotated[WebsiteRepository, Depends()],
    ):
        self.coupon_repository = coupon_repository
        self.website_repository = website_repository

    async def create_coupon(self, coupon_data: CouponCreateSchema) -> Coupon:

        new_coupon = Coupon(
            website_id=coupon_data.website_id,
            code=coupon_data.code,
            discount_amount=coupon_data.discount_amount,
            expiration_date=coupon_data.expiration_date,
            usage_limit=coupon_data.usage_limit,
        )

        return self.coupon_repository.create_coupon(new_coupon)
        

    async def get_coupon_by_code(self, coupon_code:str) ->Coupon:
        return self.coupon_repository.get_coupon_by_code(coupon_code)
    
    async def get_coupon_by_id(self, coupon_id:str) ->Coupon:
        return self.coupon_repository.get_coupon_by_id(coupon_id)
    
    async def get_coupons_by_website_id(self, website_id: UUID) -> List[Coupon]:
        return self.coupon_repository.get_coupons_by_website_id(website_id)


    async def delete_coupon(self, coupon_id: UUID) -> None:
        self.coupon_repository.delete_coupon(coupon_id)
