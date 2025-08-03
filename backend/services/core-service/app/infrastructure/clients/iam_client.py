from typing import Annotated
from uuid import UUID
from loguru import logger
from fastapi import Depends
from core.configs.config import get_settings, Settings
from domain.schemas.token_schema import TokenDataSchema, AdminTokenDataSchema
from infrastructure.clients.http_client import HTTPClient


class IAMClient:
    def __init__(
            self,
            http_client: Annotated[HTTPClient, Depends()],
            config: Settings = Depends(get_settings),
    ):
        self.config = config
        self.http_client = http_client

    async def validate_user_token(self, token: str) -> TokenDataSchema:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.http_client as client:
            response = await client.get(
                f"{self.config.IAM_URL}/api/v1/users/Me", headers=headers
            )
            response.raise_for_status()
            logger.info(f"Token {token} validated")
            return TokenDataSchema(**response.json())


    
    async def validate_buyer_token(self, token: str, website_id:str) -> TokenDataSchema:
        headers = {"Authorization": f"Bearer {token}",
                "X-Website-Id": website_id,}
        async with self.http_client as client:
            response = await client.get(
                f"{self.config.IAM_URL}/api/v1/buyers/Me", headers=headers
            )
            response.raise_for_status()
            logger.info(f"Token {token} validated")
            return TokenDataSchema(**response.json())        


    async def validate_admin_token(self, token: str) -> AdminTokenDataSchema:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.http_client as client:
            response = await client.get(
                f"{self.config.IAM_URL}/api/v1/admins/Me", headers=headers
            )
            response.raise_for_status()
            logger.info(f"Token {token} validated")
            return AdminTokenDataSchema(**response.json())                