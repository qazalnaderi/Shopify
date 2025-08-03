from datetime import datetime, timedelta, timezone
from typing import Annotated
from loguru import logger
import jwt
from fastapi import Depends, HTTPException, status
from services.buyer_service import BuyerService
from domain.schemas.token_schema import TokenDataSchema, TokenSchema
from domain.schemas.admin_schema import AdminLoginSchema
from domain.schemas.buyer_schema import BuyerLoginSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from domain.models.buyer_model import Buyer
http_bearer = HTTPBearer() 


async def get_current_buyer(
    buyer_service: Annotated[BuyerService, Depends()],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),  

) -> Buyer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Validating token for Buyer {token}")
    
    try:
        payload = jwt.decode(
            token.credentials,
            buyer_service.config.JWT_SECRET_KEY,
            algorithms=[buyer_service.config.JWT_ALGORITHM],
        )
        buyer_id: str = payload.get("sub")
        role: str = payload.get("role")  

        if role != "buyer":
            raise credentials_exception

        buyer = await buyer_service.get_buyer_by_id(buyer_id)
        if not buyer:
            logger.error("buyer not found")
            raise credentials_exception

    except jwt.PyJWTError:
        logger.error("Error decoding token")
        raise credentials_exception

    logger.info(f"buyer with id {buyer_id} validated successfully")
    return buyer