from datetime import datetime, timedelta, timezone
from typing import Annotated
from loguru import logger
import jwt
from fastapi import Depends, HTTPException, status
from domain.models.user_model import User
from domain.models.buyer_model import Buyer
from domain.models.admin_model import Admin
from services.auth_services.hash_service import HashService
from services.base_service import BaseService
from services.user_service import UserService
from services.buyer_service import BuyerService
from services.admin_service import AdminService
from domain.schemas.token_schema import TokenSchema
from domain.schemas.user_schema import UserLoginSchema
from domain.schemas.buyer_schema import BuyerLoginSchema
from domain.schemas.admin_schema import AdminLoginSchema
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

http_bearer = HTTPBearer() 
        
class AuthService(BaseService):
    def __init__(
        self,
        hash_service: Annotated[HashService, Depends()],
        user_service: Annotated[UserService, Depends()],
        buyer_service: Annotated[BuyerService, Depends()],
        admin_service: Annotated[AdminService, Depends()],
    ) -> None:
        super().__init__()
        self.user_service = user_service
        self.buyer_service = buyer_service
        self.hash_service = hash_service
        self.admin_service = admin_service

    async def authenticate_user(self, user: UserLoginSchema) -> TokenSchema:
        existing_user = await self.user_service.get_user_by_email(
            user.email
        )
        logger.info(f"Authenticating user with email: {user.email}")

        if not existing_user:
            logger.error(f"User with email {user.email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
            )

        if not existing_user.is_verified:
            logger.error(f"User with email {user.email} is not verified")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is not verified"
            )

        if not self.hash_service.verify_password(
            user.password, existing_user.password
        ):
            logger.error(f"Invalid password for user with email {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = self.create_access_token(data={"sub": str(existing_user.user_id), "role": "user"})

        logger.info(f"User with email {user.email} authenticated successfully")
        return TokenSchema(access_token=access_token, token_type="bearer")


    async def authenticate_buyer(self, buyer: BuyerLoginSchema) -> TokenSchema:
    
        existing_buyer = await self.buyer_service.get_buyer_by_email(buyer.website_id, buyer.email)
        logger.info(f"Authenticating buyer with email: {buyer.email}")

        if not existing_buyer:
            logger.error(f"Buyer with email {buyer.email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Buyer does not exist"
            )

        if not existing_buyer.is_verified:
            logger.error(f"Buyer with email {buyer.email} is not verified")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Buyer is not verified"
            )

        if not self.hash_service.verify_password(buyer.password, existing_buyer.password):
            logger.error(f"Invalid password for buyer with email {buyer.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = self.create_access_token(data={"sub": str(existing_buyer.buyer_id), "role": "buyer"})

        logger.info(f"Buyer with email {buyer.email} authenticated successfully")
        return TokenSchema(access_token=access_token, token_type="bearer")
    


    async def authenticate_admin(self, admin: AdminLoginSchema) -> TokenSchema:
        existing_admin = await self.admin_service.get_admin_by_email(
            admin.email
        )
        logger.info(f"Authenticating admin with email: {admin.email}")

        if not existing_admin:
            logger.error(f"admin with email {admin.email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="admin does not exist"
            )


        if not self.hash_service.verify_password(
            admin.password, existing_admin.password
        ):
            logger.error(f"Invalid password for admin with email {admin.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect adminname or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = self.create_access_token(data={"sub": str(existing_admin.admin_id), "role": "admin"})

        logger.info(f"admin with email {admin.email} authenticated successfully")
        return TokenSchema(access_token=access_token, token_type="bearer")

    

    def create_access_token(self, data: dict) -> str:
        logger.info("Creating access token")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            self.config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM
        )
        return encoded_jwt


async def get_current_user(
    user_service: Annotated[UserService, Depends()],
    token: HTTPAuthorizationCredentials = Depends(http_bearer), 

) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Validating token for user {token}")
    
    try:

        payload = jwt.decode(
            token.credentials,
            user_service.config.JWT_SECRET_KEY,
            algorithms=[user_service.config.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        role: str = payload.get("role") 

        if role != "user":
            raise credentials_exception

        user = await user_service.get_user_by_id(user_id)
        if not user:
            logger.error("User not found")
            raise credentials_exception

    except jwt.PyJWTError:
        logger.error("Error decoding token")
        raise credentials_exception

    logger.info(f"User with id {user_id} validated successfully")
    return user


async def get_current_buyer(
    buyer_service: Annotated[BuyerService, Depends()],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),  

) -> Buyer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Validating token for buyer {token}")
    
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



async def get_current_admin(
    admin_service: Annotated[AdminService, Depends()],
    token: HTTPAuthorizationCredentials = Depends(http_bearer),  

) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Validating token for admin {token}")
    
    try:
        payload = jwt.decode(
            token.credentials,
            admin_service.config.JWT_SECRET_KEY,
            algorithms=[admin_service.config.JWT_ALGORITHM],
        )
        admin_id: str = payload.get("sub")
        role: str = payload.get("role")  

        if role != "admin":
            raise credentials_exception

        admin = await admin_service.get_admin_by_id(admin_id)
        if not admin:
            logger.error("admin not found")
            raise credentials_exception

    except jwt.PyJWTError:
        logger.error("Error decoding token")
        raise credentials_exception

    logger.info(f"admin with id {admin_id} validated successfully")
    return admin
