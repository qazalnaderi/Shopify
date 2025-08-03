from services.website_service import WebsiteService
from services.user_service import UserService
from domain.schemas.website_schema import (WebsiteResponseSchema, WebsiteCreateSchema,
                                                WebsiteCategoryCreateSchema,WebsiteCategoryResponseSchema,
                                                  WebsiteSubcategoryCreateSchema,CategoryUpdateSchema,WebsiteUpdateSchema,
                                                  SubCategoryUpdateSchema,
WebsiteSubcategoryResponseSchema, MessageResponse,
OrderInvoiceSchema,AddWebsiteOwnerSchema)
from uuid import UUID
from fastapi import HTTPException, Depends
from loguru import logger
from services.base_service import BaseService
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from typing import List, Dict
from services.plan_service import PlanService
import jdatetime
from dateutil.relativedelta import relativedelta
from utils.date_utils import get_jalali_month_year
from datetime import date

class WebsiteMainService(BaseService):
    def __init__(
        self,
        website_service: Annotated[WebsiteService, Depends()],
        user_service: Annotated[UserService, Depends()],
        plan_service: Annotated[PlanService, Depends()],
    ) -> None:
        super().__init__()
        self.website_service = website_service
        self.user_service = user_service
        self.plan_service = plan_service


    async def create_website(self, user_id: UUID, website_data: WebsiteCreateSchema) -> WebsiteResponseSchema:
        logger.info(f"Starting to create website for user {user_id} with data: {website_data.dict()}")

        website = await self.user_service.check_is_owner(user_id)
        if website:
            raise HTTPException(status_code=409, detail="You only can own one website")

        created_website = await self.website_service.create_website(user_id, website_data)
        
        return WebsiteResponseSchema(
            website_id = created_website.website_id,
            business_name=created_website.business_name,
            welcome_text=created_website.welcome_text,
            guide_page=created_website.guide_page,
            store_policy= jsonable_encoder(created_website.store_policy),
            store_slogan= created_website.store_slogan,
            about_us= created_website.about_us,
            social_links=jsonable_encoder(created_website.social_links), 
            faqs=jsonable_encoder(created_website.faqs),  
            logo_url=created_website.logo_url,
            banner_image=created_website.banner_image,
        )
    



    async def create_website_category(self, website_category_data: WebsiteCategoryCreateSchema) -> WebsiteCategoryResponseSchema:
        logger.info(f"Starting to create website category with data: {website_category_data.dict()}")

        created_website_category = await self.website_service.create_website_category(website_category_data)

        return WebsiteCategoryResponseSchema(
            id=created_website_category.id,
            website_id=created_website_category.website_id,
            name=created_website_category.name,
            is_active=created_website_category.is_active,
            created_at=created_website_category.created_at,
            message="website Category Created Successfully ✅"
        )



    async def get_website_by_id(self, website_id: UUID) -> WebsiteResponseSchema:
        logger.info(f"Starting to fetch website with ID: {website_id}")

        website = await self.website_service.get_website_by_id(website_id)

        return WebsiteResponseSchema(
            website_id = website.website_id,
            business_name=website.business_name,
            welcome_text=website.welcome_text,
            about_us= website.about_us,
            guide_page=website.guide_page,
            store_policy= jsonable_encoder(website.store_policy),
            store_slogan= website.store_slogan,
            social_links=jsonable_encoder(website.social_links), 
            faqs=jsonable_encoder(website.faqs),  
            logo_url=website.logo_url,
            banner_image=website.banner_image,
        )

    async def get_website_categories_by_website_id(self, website_id: UUID) -> List[WebsiteCategoryResponseSchema]:
        logger.info(f"Fetching website categories for website ID: {website_id}")

        categories = await self.website_service.get_website_categories_by_website_id(website_id)

        return [
            WebsiteCategoryResponseSchema(
                id=cat.id,
                website_id=cat.website_id,
                name=cat.name,
                is_active=cat.is_active,
                created_at=cat.created_at
            )
            for cat in categories
        ]

    async def delete_website_category(self, category_id: UUID) -> None:
        logger.info(f"Starting to delete website category with ID: {category_id}")

        await self.website_service.delete_category_by_id(category_id)

        logger.info(f"Successfully deleted website category with ID: {category_id}")
        return {"message": "Category deleted successfully"}


    async def create_website_subcategory(self, subcategory_data: WebsiteSubcategoryCreateSchema) -> WebsiteSubcategoryResponseSchema:
        logger.info(f"Starting to create website subcategory with data: {subcategory_data.dict()}")

        try:
            created_subcategory = await self.website_service.create_website_subcategory(subcategory_data)

            return WebsiteSubcategoryResponseSchema(
                id=created_subcategory.id,
                parent_category_id=created_subcategory.parent_category_id,
                name=created_subcategory.name,
                is_active=created_subcategory.is_active,
                created_at=created_subcategory.created_at,
                message="Website subcategory created successfully ✅"
            )

        except Exception as e:
            logger.error(f"Error occurred while creating website subcategory: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating website subcategory: {str(e)}")  
        
    async def delete_website_subcategory(self, subcategory_id: UUID) -> None:
        logger.info(f"Starting to delete website subcategory with ID: {subcategory_id}")

        await self.website_service.delete_subcategory_by_id(subcategory_id)

        logger.info(f"Successfully deleted website subcategory with ID: {subcategory_id}")
        return {"message": "Subcategory deleted successfully"}


    async def get_subcategories_by_category_id(self, category_id: UUID) -> List[WebsiteSubcategoryResponseSchema]:
        logger.info(f"Fetching subcategories for category ID: {category_id}")
        
        subcategories = await self.website_service.get_subcategories_by_category_id(category_id)
        
        return [
            WebsiteSubcategoryResponseSchema(
                id=subcat.id,
                parent_category_id=subcat.parent_category_id,
                name=subcat.name,
                created_at=subcat.created_at,
                is_active=subcat.is_active
            ) for subcat in subcategories
        ]
    
    async def get_website_for_user(self, user_id: UUID) -> WebsiteResponseSchema:
        website = await self.user_service.get_website_for_user(user_id)
        return WebsiteResponseSchema(
            website_id=website.website_id,
            business_name=website.business_name,
            welcome_text=website.welcome_text,
            guide_page=website.guide_page,
            about_us= website.about_us,
            store_policy= jsonable_encoder(website.store_policy),
            store_slogan= website.store_slogan,
            social_links=jsonable_encoder(website.social_links),
            faqs=jsonable_encoder(website.faqs),
            logo_url=website.logo_url,
            banner_image=website.banner_image,
            created_at=website.created_at,
        )

    async def add_new_owner(self,owner_id: UUID ,new_owner_data: AddWebsiteOwnerSchema) -> MessageResponse:
        existing_user = await self.user_service.get_user_by_email(new_owner_data.email)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User is not a member of our platform")

        await self.website_service.add_new_owner(owner_id, existing_user.user_id, new_owner_data.website_id)   
        return MessageResponse(message="User successfully added as website owner.")
    
    async def edit_website_category(self, category_data: CategoryUpdateSchema) -> dict:
        logger.info(f"Starting to edit website category with ID: {category_data.category_id}")

        updated_category = await self.website_service.update_category_by_id(category_data)

        logger.info(f"Successfully updated website category with ID: {category_data.category_id}")
        return updated_category
    
    async def edit_website_subcategory(self, subcategory_data: SubCategoryUpdateSchema) -> dict:
        logger.info(f"Starting to edit website subcategory with ID: {subcategory_data.subcategory_id}")

        updated_subcategory = await self.website_service.update_subcategory_by_id(subcategory_data)

        logger.info(f"Successfully updated website subcategory with ID: {subcategory_data.subcategory_id}")
        return updated_subcategory
    
    async def update_website(self,updated_data:WebsiteUpdateSchema, user_id:UUID) -> WebsiteResponseSchema:
        logger.info(f"Starting to edit website with ID: {updated_data.website_id}")
        user_website = await self.user_service.get_website_for_user(user_id)
        if user_website.website_id != updated_data.website_id:
            raise HTTPException(status_code=403, detail="You don't own this website")
        

        updated_website = await self.website_service.update_website(updated_data)

        logger.info(f"Successfully updated website with ID: {updated_data.website_id}")
        
        return WebsiteResponseSchema(
                website_id=updated_website.website_id,
                business_name=updated_website.business_name,
                welcome_text=updated_website.welcome_text,
                guide_page=updated_website.guide_page,
                store_policy= jsonable_encoder(updated_website.store_policy),
                store_slogan= updated_website.store_slogan,
                about_us= updated_website.about_us,
                social_links=jsonable_encoder(updated_website.social_links), 
                faqs=jsonable_encoder(updated_website.faqs),  
                logo_url=updated_website.logo_url,
                banner_image=updated_website.banner_image,
                created_at=updated_website.created_at,
            )
    
    async def get_buyers_by_website_id(self, website_id: UUID) :
        return await self.website_service.get_buyers_by_website_id(website_id)
        
    async def get_buyers_count_by_website_id(self, website_id: UUID) -> int:
        buyers_count = await self.website_service.get_buyers_count_by_website_id(website_id)
        return buyers_count
    

    async def get_active_buyers_count_by_website_id(self, website_id: UUID) -> int:
        website_plan = await self.plan_service.get_active_plan_by_website_id(website_id)
        plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
        if plan.name != 'Pro':
            raise HTTPException(status_code=403, detail="This option is only available in pro plan.")
        active_buyers_count = await self.website_service.get_active_buyers_count_by_website_id(website_id)

        return active_buyers_count
    
    async def get_sales_summary(self, website_id: UUID, mode: str) -> dict:
        website_plan = await self.plan_service.get_active_plan_by_website_id(website_id)
        if website_plan:
            plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
            if plan.name != 'Pro':
                raise HTTPException(status_code=403, detail="This option is only available in pro plan.")
            return await self.website_service.get_sales_summary(website_id, mode)

    async def get_last_6_months_sales(self, website_id: UUID) -> List[dict]:
        website_plan = await self.plan_service.get_active_plan_by_website_id(website_id)
        plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
        if plan.name != 'Pro':
            raise HTTPException(status_code=403, detail="This option is only available in pro plan.")
        today = date.today()
        months = []

        for i in range(0,6):  
            target_gregorian = today - relativedelta(months=i)
            jalali_label = get_jalali_month_year(target_gregorian)

            year, month = target_gregorian.year, target_gregorian.month

            stats = await self.website_service.get_total_revenue_for_month(website_id, year, month)

            months.append({
                "month": jalali_label,
                "revenue": stats["revenue"]

            })


        return months
    
    async def get_total_revenue(self, website_id: UUID) -> dict:
        return await self.website_service.get_total_revenue(website_id)

    async def get_total_sales_count(self, website_id: UUID) -> int:
        return await self.website_service.get_total_sales_count(website_id)
    
    async def get_latest_orders(self, website_id: UUID, limit: int) -> list:
        return await self.website_service.get_latest_orders(website_id, limit)

    async def get_best_selling_items(self, website_id: UUID, limit: int) -> list:
        return await self.website_service.get_best_selling_items(website_id, limit)

    async def get_average_order_per_buyer(self, website_id: UUID) -> int:
        website_plan = await self.plan_service.get_active_plan_by_website_id(website_id)
        plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
        if plan.name != 'Pro':
            raise HTTPException(status_code=403, detail="This option is only available in pro plan.")
        return await self.website_service.get_average_order_per_buyer(website_id)
    
    async def get_total_buyers_count(self, website_id: UUID) -> int:
        return await self.website_service.get_total_buyers_count(website_id)

    async def get_latest_announcements(self, website_id: UUID) -> list:
        website_plan = await self.plan_service.get_active_plan_by_website_id(website_id)
        plan = await self.plan_service.get_plan_by_id(website_plan.plan_id)
        if plan.name != 'Pro':
            raise HTTPException(status_code=403, detail="This option is only available in pro plan.")
        return await self.website_service.get_latest_announcements(website_id)
    

    async def get_active_plan(self, website_id:UUID):
        return await self.plan_service.get_active_plan_by_website_id(website_id)


    async def get_order_invoice_table(self, website_id: UUID, sort_by:str) -> list:
        return await self.website_service.get_order_invoice_table(website_id, sort_by)


    async def get_website_buyers_summary(self, website_id: UUID, sort_by: str) -> list:
        return await self.website_service.get_website_buyers_summary(website_id, sort_by)
