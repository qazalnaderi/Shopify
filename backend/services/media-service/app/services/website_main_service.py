from services.website_service import WebsiteService
from services.user_service import UserService
from domain.schemas.website_schema import (WebsiteResponseSchema, WebsiteUpdateSchema)
from uuid import UUID
from fastapi import HTTPException, Depends
from loguru import logger
from services.base_service import BaseService
from typing import Annotated
from fastapi.encoders import jsonable_encoder


class WebsiteMainService(BaseService):
    def __init__(
        self,
        website_service: Annotated[WebsiteService, Depends()],
        user_service: Annotated[UserService, Depends()],
    ) -> None:
        super().__init__()
        self.website_service = website_service
        self.user_service = user_service



    async def get_website_by_id(self, website_id: UUID) -> WebsiteResponseSchema:
        logger.info(f"Starting to fetch website with ID: {website_id}")

        website = await self.website_service.get_website_by_id(website_id)

        return WebsiteResponseSchema(
            id = website.website_id,
            business_name=website.business_name,
            welcome_text=website.welcome_text,
            guide_page=website.guide_page,
            social_links=jsonable_encoder(website.social_links), 
            faqs=jsonable_encoder(website.faqs),  
            logo_url=website.logo_url,
            banner_image=website.banner_image,
            message="Website fetched successfully ✅"   
        )


    
    async def update_website(self,updated_data:WebsiteUpdateSchema, user_id:UUID) -> WebsiteResponseSchema:
        logger.info(f"Starting to edit website with ID: {updated_data.website_id}")
        user_website = await self.user_service.get_website_for_user(user_id)
        if user_website.website_id != updated_data.website_id:
            raise HTTPException(status_code=403, detail="You don't own this website")
        

        updated_website = await self.website_service.update_website(updated_data)

        logger.info(f"Successfully updated website with ID: {updated_data.website_id}")
        
        return WebsiteResponseSchema(
                id=updated_website.website_id,
                business_name=updated_website.business_name,
                welcome_text=updated_website.welcome_text,
                guide_page=updated_website.guide_page,
                social_links=jsonable_encoder(updated_website.social_links), 
                faqs=jsonable_encoder(updated_website.faqs),  
                logo_url=updated_website.logo_url,
                banner_image=updated_website.banner_image,
                created_at=updated_website.created_at,
                message="Website fetched successfully ✅"
            )
    
   