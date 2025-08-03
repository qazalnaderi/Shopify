from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from loguru import logger
from infrastructure.clients.iam_client import IAMClient
from domain.schemas.token_schema import TokenDataSchema
from core.configs.config import get_settings

config = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"https://iam-tradehub.liara.run/api/v1/users/login", scheme_name="UserOAuth2")


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        client: Annotated[IAMClient, Depends()],
) -> TokenDataSchema:
    if not token:
        logger.error("No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    logger.info(f"Validating token {token}")
    return await client.validate_user_token(token)