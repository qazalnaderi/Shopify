from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends, HTTPException
from domain.models.user_model import User
from domain.schemas.user_schema import UserCreateSchema
from infrastructure.repositories.user_repository import UserRepository
from services.auth_services.hash_service import HashService
from services.base_service import BaseService
import uuid


class UserService(BaseService):
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends()],
        hash_service: Annotated[HashService, Depends()],
    ) -> None:
        super().__init__()
        self.user_repository = user_repository
        self.hash_service = hash_service

    async def create_user(self, user_body: UserCreateSchema) -> User:
        logger.info(f"⚒️ Creating user with email: {user_body.email}")
        return self.user_repository.create_user(
            User(
                first_name=user_body.first_name,
                last_name=user_body.last_name,
                email=user_body.email,
                password=self.hash_service.hash_password(user_body.password), 
            )
        )

    async def get_user_by_email(self, email: str) -> User:
        logger.info(f"📥 Fetching user with email {email}")
        return self.user_repository.get_user_by_email(email)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:  
        logger.info(f"📥 Fetching user with id {user_id}")
        return self.user_repository.get_user_by_id(user_id)

    async def update_verified_status(self, user_id: uuid.UUID, update_fields: Dict) -> User: 
        logger.info(f"🔃 Updating user with id {user_id}")
        return self.user_repository.update_user(user_id, update_fields)

    async def update_user(self, user_id: uuid.UUID, update_fields: Dict) -> User:
        logger.info(f"🔃 Updating user with id {user_id}")
        password = update_fields.get("password")
        confirm_password = update_fields.get("confirm_password")

        if password is not None or confirm_password is not None:
            if password != confirm_password:
                raise HTTPException(status_code=400, detail="Password confirmation does not match")
            
            if not password:
                raise HTTPException(status_code=400, detail="Password cannot be empty")

            update_fields["password"] = self.hash_service.hash_password(password)

        update_fields.pop("confirm_password", None)
        
        update_fields = {
            key: value for key, value in update_fields.items()
            if value not in ("", None)
        }

        return self.user_repository.update_user(user_id, update_fields)  

    async def update_can_change_status(self, user_id: uuid.UUID, update_fields: Dict) -> User: 
        logger.info(f"🔃 Updating user with id {user_id}")
        return self.user_repository.update_user(user_id, update_fields)

    async def change_user_password(self, email:str, update_fields: Dict) -> User:
        logger.info(f"🔃 Changing password user with id {email}")

        if update_fields['password'] != update_fields['confirm_password']:
            logger.info(f"❌ Password confirmation does not match")
            raise HTTPException(status_code=400, detail='Password confirmation does not match')
        update_fields['password'] = self.hash_service.hash_password(update_fields['password'])
        update_fields.pop('confirm_password')

        user = self.user_repository.get_user_by_email(email)
        if user.can_reset_password != True:
            raise HTTPException(status_code=400, detail='You need to verify the otp first')

        self.user_repository.update_user(user.user_id, {"can_reset_password": False})    
        return self.user_repository.update_user(user.user_id, update_fields)
