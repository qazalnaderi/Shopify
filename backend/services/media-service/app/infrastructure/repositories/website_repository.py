from domain.models.website_model import Website
from sqlalchemy.orm import Session
from loguru import logger
from uuid import UUID
from core.postgres_db.postgres_database import get_db
from typing import Annotated
from fastapi import Depends
from typing import List, Optional
from sqlalchemy import func


class WebsiteRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db
        


    def get_website_by_id(self, website_id: UUID) -> Website:
        website = self.db.query(Website).filter(Website.website_id == website_id).first()

        if not website :
            logger.warning(f"⚠️ No website found with id: {website_id}")
        else:
            logger.info(f"✅ Website found with id: {website_id}")

        return website   


    def update_website(self,website: Website) -> Website:

        updated_website = self.get_website_by_id(website.website_id)
        self.db.add(website)
        self.db.commit()
        self.db.refresh(website)
        logger.info(f"✅ website with ID {website.website_id} successfully updated in the database.")   
        return updated_website        
    