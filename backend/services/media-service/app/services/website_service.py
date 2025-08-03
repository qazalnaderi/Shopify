from infrastructure.repositories.website_repository import WebsiteRepository
from domain.schemas.website_schema import  WebsiteUpdateSchema
from uuid import UUID
from fastapi import HTTPException, Depends
from services.base_service import BaseService
from typing import Annotated
from loguru import logger
from domain.models.website_model import Website

class WebsiteService(BaseService):
    def __init__(
        self,
        website_repository: Annotated[WebsiteRepository, Depends()],
    ) -> None:
        super().__init__()  
        self.website_repository = website_repository




    async def get_website_by_id(self, website_id: UUID) -> Website:
        logger.info(f"Starting to fetch website with ID: {website_id}")

        try:
            website = self.website_repository.get_website_by_id(website_id)

            if not website  :
                logger.warning(f"⚠️ No website found with id: {website_id}")
                raise HTTPException(status_code=404, detail="Website not found")

            return website

        except Exception as e:
            logger.error(f"Error occurred while fetching website with ID {website_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching website: {str(e)}")        

        

                
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
        except Exception as e:
            logger.error(f"Error updating Website with ID {updated_data.website_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating Website: {str(e)}")
        
  