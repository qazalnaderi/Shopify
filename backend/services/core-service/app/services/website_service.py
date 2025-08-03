from infrastructure.repositories.website_repository import WebsiteRepository, WebsiteSubcategory, WebsiteOwner
from infrastructure.repositories.buyer_repository import BuyerRepository
from domain.models.website_model import Website, WebsiteCategory
from domain.schemas.website_schema import (WebsiteCreateSchema, WebsiteUpdateSchema,
WebsiteCategoryCreateSchema, SubCategoryResponseSchema, SubCategoryUpdateSchema,WebsiteResponseSchema,
CategoryUpdateSchema, CategoryResponseSchema, WebsiteSubcategoryCreateSchema)
from uuid import UUID
from fastapi import HTTPException, Depends
from services.base_service import BaseService
from typing import Annotated
from loguru import logger
from fastapi.encoders import jsonable_encoder
from typing import List, Dict
from infrastructure.repositories.order_repository import OrderRepository
from datetime import date



class WebsiteService(BaseService):
    def __init__(
        self,
        website_repository: Annotated[WebsiteRepository, Depends()],
        buyer_repository: Annotated[BuyerRepository, Depends()],
        order_repository: Annotated[OrderRepository, Depends()],
    ) -> None:
        super().__init__()  
        self.website_repository = website_repository
        self.buyer_repository = buyer_repository
        self.order_repository = order_repository




    async def create_website(self, user_id: UUID, website_data: WebsiteCreateSchema) -> Website:
        
        created_website = self.website_repository.create_website(website=Website(
            business_name=website_data.business_name,
            welcome_text=website_data.welcome_text,
            guide_page=website_data.guide_page,
            store_policy= jsonable_encoder(website_data.store_policy),
            store_slogan= website_data.store_slogan,
            social_links=jsonable_encoder(website_data.social_links), 
            faqs=jsonable_encoder(website_data.faqs),  
        ))
        logger.info(f"Website created successfully with ID: {created_website.website_id}")

        website_owner = self.website_repository.create_website_owner(user_id, created_website.website_id)
        logger.info(f"website owner created with ID: {website_owner.user_id}")
        return created_website

        
    async def create_website_category(self, website_category_data: WebsiteCategoryCreateSchema) -> WebsiteCategory:
        logger.info(f"Starting to create store category with data: {website_category_data.dict()}")

        new_website_category = self.website_repository.create_website_category(
            website_category=WebsiteCategory(
                website_id=website_category_data.website_id,
                name=website_category_data.name,
            )
        )
        return new_website_category


    async def get_website_categories_by_website_id(self, website_id: UUID) -> List[WebsiteCategory]:
        logger.info(f"Fetching categories for website ID: {website_id}")

        categories = self.website_repository.get_website_categories_by_website_id(website_id)
        return categories


    async def delete_category_by_id(self, category_id: UUID) -> None:
        logger.info(f"Attempting to delete category with ID: {category_id}")
        
        category = self.website_repository.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        self.website_repository.delete_category(category_id)
        logger.info(f"Category with ID {category_id} successfully deleted.")



    async def get_website_by_id(self, website_id: UUID) -> Website:
        logger.info(f"Starting to fetch website with ID: {website_id}")

        website = self.website_repository.get_website_by_id(website_id)

        if not website  :
            logger.warning(f"⚠️ No website found with id: {website_id}")
            raise HTTPException(status_code=404, detail="Website not found")

        return website


    async def create_website_subcategory(self, subcategory_data: WebsiteSubcategoryCreateSchema) -> WebsiteSubcategory:
        logger.info(f"Starting to create website subcategory with data: {subcategory_data.dict()}")
        new_subcategory = self.website_repository.create_website_subcategory(
            subcategory=WebsiteSubcategory(
                parent_category_id=subcategory_data.parent_category_id,
                name=subcategory_data.name
            )
        )
        return new_subcategory


    async def get_subcategories_by_category_id(self, category_id: UUID) -> List[WebsiteSubcategory]:
        logger.info(f"Fetching subcategories for category ID: {category_id}")
        
        subcategories = self.website_repository.get_subcategories_by_category_id(category_id)        
        return subcategories
    async def get_subcategory_by_id(self, subcategory_id: UUID) -> WebsiteSubcategory:
        return self.website_repository.get_subcategory_by_id(subcategory_id)
            
    async def get_category_by_id(self, category_id: UUID) -> WebsiteCategory:
        return self.website_repository.get_category_by_id(category_id)

    async def add_new_owner(self,owner_id: UUID ,user_id: UUID, website_id: UUID) -> WebsiteOwner:
        website_owner = self.website_repository.get_owner_by_user_and_website(owner_id, website_id)
        if not website_owner:
            raise HTTPException(status_code=403, detail="You are not the owner of this website and cannot add owners.")

        existing_owner = self.website_repository.get_owner(user_id)
        if existing_owner:
            raise HTTPException(status_code=409, detail="User already owns a website.")
        new_owner = self.website_repository.create_website_owner(user_id, website_id)
        return new_owner

    async def update_category_by_id(self, category_data: CategoryUpdateSchema) -> dict:
        logger.info(f"Attempting to update category with ID: {category_data.category_id}")
        
        try:
            category = self.website_repository.get_category_by_id(category_data.category_id)

            update_data = category_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(category, key, value)

            self.website_repository.update_category(category)

            logger.info(f"Category with ID {category_data.category_id} successfully updated.")

            return CategoryResponseSchema.from_orm(category)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"Error updating category with ID {category_data.category_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")
        
    async def update_subcategory_by_id(self, subcategory_data: SubCategoryUpdateSchema) -> dict:
        logger.info(f"Attempting to update category with ID: {subcategory_data.subcategory_id}")
        
        try:
            subcategory = self.website_repository.get_subcategory_by_id(subcategory_data.subcategory_id)

            update_data = subcategory_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(subcategory, key, value)

            self.website_repository.update_subcategory(subcategory)

            logger.info(f"subcategory with ID {subcategory_data.subcategory_id} successfully updated.")

            return SubCategoryResponseSchema.from_orm(subcategory)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"Error updating subcategory with ID {subcategory_data.category_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating subcategory: {str(e)}")
        

    async def delete_subcategory_by_id(self, subcategory_id: UUID) -> None:
        logger.info(f"Attempting to delete category with ID: {subcategory_id}")
        
        try:
            subcategory = self.website_repository.get_subcategory_by_id(subcategory_id)
            
            if not subcategory:
                raise HTTPException(status_code=404, detail="Category not found")

            self.website_repository.delete_subcategory(subcategory_id)
            logger.info(f"Suncategory with ID {subcategory_id} successfully deleted.")

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"Error deleting subcategory with ID {subcategory_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting subcategory: {str(e)}")
        

                
    async def update_website(self,updated_data: WebsiteUpdateSchema) -> Website:
        logger.info(f"Attempting to update website with ID: {updated_data.website_id}")
        
        try:
            Website = self.website_repository.get_website_by_id(updated_data.website_id)

            update_data = updated_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(Website, key, value)

            updated_website = self.website_repository.update_website(Website)

            logger.info(f"Website with ID {updated_data.website_id} successfully updated.")

            return updated_website

        # except HTTPException as http_exc:
        #     raise http_exc

        except Exception as e:
            logger.error(f"Error updating Website with ID {updated_data.website_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating Website: {str(e)}")
        
    async def get_buyers_by_website_id(self, website_id: UUID) -> List[Dict]:
        logger.info(f"Starting to fetch website with ID: {website_id}")

        try:
            website = self.website_repository.get_website_by_id(website_id)
            buyers = self.order_repository.get_buyers_by_website_id(website.website_id)
            return buyers
        
        except Exception as e:
            logger.error(f"Error occurred while fetching buyers fo website with ID {website_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching buyers : {str(e)}")        

        
    async def get_buyers_count_by_website_id(self, website_id: UUID) -> int:
        Website = self.website_repository.get_website_by_id(website_id)
        return self.buyer_repository.get_buyers_count_by_website_id(website_id)
    

    async def get_active_buyers_count_by_website_id(self, website_id: UUID) -> int:
        website = self.website_repository.get_website_by_id(website_id)
        return self.order_repository.get_active_buyers_count_by_website(website_id)
    

    async def get_sales_summary(self, website_id: UUID, mode: str) -> dict:
        today = date.today()

        if mode == "daily":
            return self.order_repository.get_sales_by_day(website_id, today)

        elif mode == "monthly":
            logger.info(f"{today.year}, {today.month}")
            return self.order_repository.get_sales_by_month(website_id, today.year, today.month)

        elif mode == "yearly":
            return self.order_repository.get_sales_by_year(website_id, today.year)

        else:
            raise ValueError("Invalid mode")
        


    async def get_total_revenue_for_month(self, website_id: UUID, year: int, month: int) -> List[dict]:
        logger.info(f"year :{year} , month: {month}")
        return self.order_repository.get_sales_by_month(website_id, year, month)


    async def get_total_revenue(self, website_id: UUID) -> dict:
        return self.order_repository.get_total_revenue(website_id)
    

    async def get_total_sales_count(self, website_id: UUID) -> int:
        return self.order_repository.get_total_sales_count(website_id)


    async def get_latest_orders(self, website_id: UUID, limit: int) -> list:
     return self.order_repository.get_latest_orders(website_id, limit)


    async def get_best_selling_items(self, website_id: UUID, limit: int) -> list:
        return self.order_repository.get_best_selling_items(website_id, limit)

    async def get_total_buyers_count(self, website_id: UUID) -> int:
        return self.website_repository.get_total_buyers_count(website_id)
    

    async def get_average_order_per_buyer(self, website_id: UUID) -> int:
        buyers_count = await self.get_total_buyers_count(website_id)
        return self.order_repository.get_average_order_per_buyer(website_id, buyers_count)
    

    async def get_latest_announcements(self, website_id: UUID) -> list:
        return self.website_repository.get_latest_announcements(website_id)
    
    async def get_website_owner_email(self, website_id:UUID) :
        return self.website_repository.get_website_owner_email(website_id)
    

    async def get_all_websites(self) -> list[Website]:
        return self.website_repository.get_all_websites()


    async def get_order_invoice_table(self, website_id: UUID, sort_by:str) -> list:
        return self.order_repository.get_order_invoice_table(website_id, sort_by)
    

    async def get_website_buyers_summary(self, website_id: UUID, sort_by: str) -> list:
        return self.order_repository.get_website_buyers_summary(website_id, sort_by)
