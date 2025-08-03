
from fastapi import APIRouter, Depends,Query 
from services.admin_main_service import AdminMainService
from domain.schemas.admin_schema import ShopPlanStatsSchema, TopWebsiteSchema, WebsiteListSchema, RevenueStatsSchema, RevenueTrendSchema
from typing import Annotated, List
from services.auth_services.admin_auth_service import get_current_admin
from domain.schemas.token_schema import AdminTokenDataSchema
from loguru import logger


admin_router = APIRouter()

@admin_router.get("/dashboard/stats", response_model=ShopPlanStatsSchema)
async def get_dashboard_stats(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)]
):
    return await admin_main_service.get_shop_plan_stats()


@admin_router.get("/dashboard/user-seller-stats")
async def get_user_and_seller_stats(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)]
):
    return await admin_main_service.get_user_and_seller_stats()


@admin_router.get("/dashboard/revenue")
async def get_revenue(
    admin_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)]):
    
    return {"total_revenue": await admin_service.get_total_revenue()}


@admin_router.get("/dashboard/website-activity")
async def get_website_activity_stats(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)]
):
    return await admin_main_service.get_website_activity_stats()


@admin_router.get("/dashboard/top-websites", response_model=List[TopWebsiteSchema])
async def get_top_websites(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
    sort_by: str = Query("income", enum=["income", "sales"]),
    limit: int = Query(5, gt=0, le=20)
):
    return await admin_main_service.get_top_websites(sort_by=sort_by, limit=limit)



@admin_router.get("/dashboard/websites", response_model=List[WebsiteListSchema])
async def get_websites_table(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
    sort_by: str = Query("created_at", enum=["created_at", "revenue"]),
):
    return await admin_main_service.get_website_table(sort_by)



@admin_router.get("/dashboard/revenue-stats", response_model=RevenueStatsSchema)
async def get_revenue_stats(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
):
    return await admin_main_service.get_revenue_stats()


@admin_router.get("/dashboard/revenue_trend", response_model=RevenueTrendSchema)
async def get_revenue_trend(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
):
    return await admin_main_service.get_last_6_months_revenue_trend()


@admin_router.get("/dashboard/plan-revenue")
async def get_plan_revenue_breakdown(
    admin_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
):
    return await admin_service.get_plan_revenue_breakdown()


@admin_router.get("/dashboard/plan-purchase-stats")
async def get_plan_purchase_stats(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema,Depends(get_current_admin)],
):
    return await admin_main_service.get_plan_purchase_stats()

@admin_router.get("/dashboard/monthly-growth", response_model=float)
async def get_monthly_revenue_growth(
    admin_main_service: Annotated[AdminMainService, Depends()],
    current_admin: Annotated[AdminTokenDataSchema, Depends(get_current_admin)],
):
    return await admin_main_service.get_monthly_revenue_growth()
