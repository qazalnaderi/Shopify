from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends, HTTPException
from domain.models.website_model import  Website
from domain.models.user_model import User
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.website_repository import WebsiteRepository
from services.base_service import BaseService
from uuid import UUID


class UserService(BaseService):
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends()],
        website_repository: Annotated[WebsiteRepository, Depends()],

    ) -> None:
        super().__init__()
        self.user_repository = user_repository
        self.website_repository = website_repository

    async def get_user_by_email(self, email: str) -> User:
        logger.info(f"📥 Fetching user with email {email}")
        return self.user_repository.get_user_by_email(email)

    async def get_user_by_id(self, user_id: UUID) -> User:  
        logger.info(f"📥 Fetching user with id {user_id}")
        return self.user_repository.get_user_by_id(user_id)
    
    async def get_website_for_user(self, user_id: UUID) -> Website:
        logger.info(f"📥 Fetching website for user with id {user_id}")
        website = self.user_repository.get_website_by_user_id(user_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found for this user")
        return website
    
    async def check_is_owner(self, user_id: UUID) -> Website:
        logger.info(f"📥 Fetching website for user with id {user_id}")
        website = self.user_repository.get_website_by_user_id(user_id)
        return website

