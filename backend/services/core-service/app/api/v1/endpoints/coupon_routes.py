from fastapi import APIRouter, Depends, status
from services.auth_services.user_auth_service import get_current_user
from services.auth_services.buyer_auth_service import get_current_buyer
from domain.schemas.token_schema import TokenDataSchema
from loguru import logger
from typing import Annotated, List
from domain.schemas.coupon_schema import CouponCreateSchema, CouponResponseSchema
from services.coupon_main_service import CouponMainService
from uuid import UUID

coupon_router = APIRouter()

@coupon_router.post("/create_coupon", response_model=CouponResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreateSchema,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    coupon_service: Annotated[CouponMainService, Depends()]
):
    logger.info(f"User with id: {current_user.user_id} is creating a coupon.")
    return await coupon_service.create_coupon(coupon_data)


@coupon_router.get("/website/{website_id}/coupons", response_model=List[CouponResponseSchema])
async def get_coupons_by_website(
    website_id: UUID,
    coupon_main_service: Annotated[CouponMainService, Depends()]
):
    return await coupon_main_service.get_coupons_by_website_id(website_id)


@coupon_router.delete("/coupon/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    coupon_main_service: Annotated[CouponMainService, Depends()]
):
    await coupon_main_service.delete_coupon(coupon_id)
    return {}
