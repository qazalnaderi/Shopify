from typing import Annotated, Dict
from loguru import logger
from fastapi import Depends, HTTPException
from domain.models.buyer_model import Buyer
from domain.schemas.buyer_schema import BuyerCreateSchema
from infrastructure.repositories.buyer_repository import BuyerRepository
from services.auth_services.hash_service import HashService
from services.base_service import BaseService
import uuid


class BuyerService(BaseService):
    def __init__(
        self,
        buyer_repository: Annotated[BuyerRepository, Depends()],
        hash_service: Annotated[HashService, Depends()],
    ) -> None:
        super().__init__()
        self.buyer_repository = buyer_repository
        self.hash_service = hash_service


    async def create_buyer(self, buyer_body: BuyerCreateSchema) -> Buyer:
        logger.info(f"⚒️ Creating buyer with email: {buyer_body.email}")
        return self.buyer_repository.create_buyer(
            Buyer(
                name=buyer_body.name,
                email=buyer_body.email,
                password_hash=self.hash_service.hash_password(buyer_body.password),  # Hash the password
            )
        )

    async def get_buyer_by_email(self, email: str) -> Buyer:
        logger.info(f"📥 Fetching buyer with email {email}")
        return self.buyer_repository.get_buyer_by_email(email)

    async def get_buyer_by_id(self, buyer_id: uuid.UUID) -> Buyer:  
        logger.info(f"📥 Fetching buyer with id {buyer_id}")
        return self.buyer_repository.get_buyer_by_id(buyer_id)

    async def update_verified_status(self, buyer_id: uuid.UUID, update_fields: Dict) -> Buyer: 
        logger.info(f"🔃 Updating buyer with id {buyer_id}")
        return self.buyer_repository.update_buyer(buyer_id, update_fields)

    async def update_buyer(self, buyer_id: uuid.UUID, update_fields: Dict) -> Buyer:
        logger.info(f"🔃 Updating buyer with id {buyer_id}")

        if 'password' in update_fields:
            if update_fields['password'] != update_fields['confirm_password']:
                logger.info(f"❌ Password confirmation does not match")
                raise HTTPException(status_code=400, detail='Password confirmation does not match')
        update_fields['password_hash'] = self.hash_service.hash_password(update_fields['password'])
        update_fields.pop('confirm_password')
        
        update_fields = {key: value for key, value in update_fields.items() if value != ""}  

        return self.buyer_repository.update_buyer(buyer_id, update_fields)

    async def update_can_reset_password_status(self, buyer_id: uuid.UUID, update_fields: Dict) -> Buyer: 
        logger.info(f"🔃 Updating buyer with id {buyer_id}")
        return self.buyer_repository.update_buyer(buyer_id, update_fields)

    async def change_buyer_password(self, email: str, update_fields: Dict) -> Buyer:
        logger.info(f"🔃 Changing password for buyer with email {email}")

        if update_fields['password'] != update_fields['confirm_password']:
            logger.info(f"❌ Password confirmation does not match")
            raise HTTPException(status_code=400, detail='Password confirmation does not match')
        
        update_fields['password_hash'] = self.hash_service.hash_password(update_fields['password'])
        update_fields.pop('confirm_password')

        buyer = self.buyer_repository.get_buyer_by_email(email)
        if not buyer or not buyer.can_reset_password:
            raise HTTPException(status_code=400, detail='You need to verify the OTP first')

        self.buyer_repository.update_buyer(buyer.buyer_id, {"can_reset_password": False})    
        return self.buyer_repository.update_buyer(buyer.buyer_id, update_fields)
