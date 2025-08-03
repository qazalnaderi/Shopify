from fastapi import HTTPException, Depends
from domain.schemas.coupon_schema import CouponCreateSchema, CouponResponseSchema
from domain.models.website_model import Coupon
from services.coupon_service import  CouponService
from uuid import UUID
from services.website_service import WebsiteService
from typing import Annotated, List
from loguru import logger


class CouponMainService:
    def __init__(
        self,
        service: Annotated[CouponService, Depends()],
        website_service: Annotated[WebsiteService, Depends()],
    ):
        self.service = service
        self.website_service = website_service

    async def create_coupon(self, coupon_data: CouponCreateSchema) -> CouponResponseSchema:
        
        logger.info(f"Starting create_coupon with data: {coupon_data.dict()}")

        website = await self.website_service.get_website_by_id(coupon_data.website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        created = await self.service.create_coupon(coupon_data)
        return CouponResponseSchema.from_orm(created)

    async def get_coupon_by_code(self, coupon_code:str) ->CouponResponseSchema:
        coupon = await  self.service.get_coupon_by_code(coupon_code)
        return CouponResponseSchema.from_orm(coupon)


    async def get_coupons_by_website_id(self, website_id: UUID) -> List[CouponResponseSchema]:
        website = await self.website_service.get_website_by_id(website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")

        coupons = await self.service.get_coupons_by_website_id(website_id)
        return [CouponResponseSchema.from_orm(c) for c in coupons]


    async def delete_coupon(self, coupon_id: UUID) -> None:
        coupon = await self.service.get_coupon_by_id(coupon_id)
        if not coupon:
            raise HTTPException(status_code=404, detail="Coupon not found")

        return await self.service.delete_coupon(coupon_id)
