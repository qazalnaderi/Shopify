from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from loguru import logger
from uuid import UUID

from domain.models.buyer_model import Buyer
from domain.schemas.buyer_schema import (
    BuyerCreateSchema,
    BuyerResponseSchema,
    VerifyOTPSchema,
    VerifyOTPResponseSchema,
    BuyerLoginSchema,
    BuyerInfoSchema,
    ResendOTPResponseSchema,
    ResendOTPSchema,
    UpdateBuyerInfoSchema,
    ForgetPasswordSchema
)
from domain.schemas.token_schema import TokenSchema, TokenDataSchema
from services.auth_services.auth_service import AuthService
from services.buyer_main_service import RegisterService
from services.auth_services.auth_service import get_current_buyer

buyer_router = APIRouter()

@buyer_router.post(
    "/Register",
    response_model=BuyerResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    buyer: BuyerCreateSchema, register_service: Annotated[RegisterService, Depends()]
) -> BuyerResponseSchema:
    logger.info(f"Registering buyer with email:{buyer.email}")
    return await register_service.register_buyer(buyer)


@buyer_router.post(
    "/VerifyOTP", response_model=TokenSchema, status_code=status.HTTP_200_OK
)
async def verify_otp(
    verify_buyer_schema: VerifyOTPSchema,
    register_service: Annotated[RegisterService, Depends()],
) -> TokenSchema:
    logger.info(f"Verifying OTP for buyer with email {verify_buyer_schema.email}")
    return await register_service.verify_buyer(verify_buyer_schema)

@buyer_router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    website_id:UUID,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends()],
) -> TokenSchema:
    logger.info(f"Logging in buyer with email {form_data.username}")
    return await auth_service.authenticate_buyer(
        BuyerLoginSchema(website_id=website_id, email=form_data.username, password=form_data.password)
    )    

@buyer_router.post(
    "/ResendOTP",
    response_model=ResendOTPResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    resend_otp_schema: ResendOTPSchema,
    register_service: Annotated[RegisterService, Depends()],
) -> ResendOTPResponseSchema:
    logger.info(f"Resending OTP for buyer with email {resend_otp_schema.email}")
    return await register_service.resend_otp(resend_otp_schema)


@buyer_router.put(
    "/UpdateProfile",
    status_code=status.HTTP_200_OK)
async def update_profile(
        current_user: Annotated[TokenDataSchema, Depends(get_current_buyer)],
        buyer_data: UpdateBuyerInfoSchema,
        buyer_service: Annotated[RegisterService, Depends()]
):
    logger.info(f'🔃 Changing buyer info for buyer {current_user.buyer_id}')
    return await buyer_service.update_buyer(current_user.buyer_id, dict(buyer_data))   


@buyer_router.get("/Me", response_model=BuyerInfoSchema, status_code=status.HTTP_200_OK)
async def read_me(current_user: Buyer = Depends(get_current_buyer)) -> BuyerInfoSchema:
    logger.info(f"📥 Getting buyer with email {current_user.email}")
    return current_user


@buyer_router.post(
    "/VerifyOTPForgetPassword", status_code=status.HTTP_200_OK
)
async def verify_otp_for_password(
    verify_buyer_schema: VerifyOTPSchema,
    register_service: Annotated[RegisterService, Depends()],
) :
    logger.info(f"Verifying OTP for buyer with email {verify_buyer_schema.email}")
    return await register_service.verify_otp_forget_password(verify_buyer_schema)

@buyer_router.put(
    "/ForgetPassword",
    status_code=status.HTTP_200_OK)
async def forget_password(
        buyer_data: ForgetPasswordSchema,
        buyer_service: Annotated[RegisterService, Depends()]
):
    logger.info(f'🔃 Changing buyer password for buyer {buyer_data.email}')
    return await buyer_service.change_buyer_password(buyer_data.email, dict(buyer_data))
