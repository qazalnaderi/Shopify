from domain.schemas.admin_schema import AdminLoginSchema, AdminResponseSchema, VerifyOTPResponseSchema, VerifyOTPSchema, ForgetPasswordSchema, ResendOTPResponseSchema, ResendOTPSchema
from domain.schemas.token_schema import TokenSchema, TokenDataSchema
from services.auth_services.auth_service import AuthService
from services.admin_service import AdminService
from services.admin_auth_service import AdminAuthService
from services.auth_services.auth_service import get_current_admin
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from loguru import logger
from domain.models.admin_model import Admin
admin_router = APIRouter()

@admin_router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends()],
) -> TokenSchema:

    logger.info(f"Logging in admin with email {form_data.username}")
    return await auth_service.authenticate_admin(
        AdminLoginSchema(email=form_data.username, password=form_data.password)
    )    

@admin_router.post(
    "/VerifyOTP", response_model=VerifyOTPResponseSchema, status_code=status.HTTP_200_OK
)
async def verify_otp(
    verify_admin_schema: VerifyOTPSchema,
    admin_service: Annotated[AdminAuthService, Depends()],
) -> VerifyOTPResponseSchema:
    logger.info(f"Verifying OTP for admin with email {verify_admin_schema.email}")
    return await admin_service.verify_admin(verify_admin_schema)

@admin_router.post(
    "/ResendOTP",
    response_model=ResendOTPResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    resend_otp_schema: ResendOTPSchema,
    admin_service: Annotated[AdminAuthService, Depends()],
) -> ResendOTPResponseSchema:
    logger.info(f"Resending OTP for admin with email {resend_otp_schema.email}")
    return await admin_service.resend_otp(resend_otp_schema)


@admin_router.post(
    "/VerifyOTPForgetPassword", status_code=status.HTTP_200_OK
)
async def verify_otp_for_password(
    verify_admin_schema: VerifyOTPSchema,
    admin_service: Annotated[AdminAuthService, Depends()],
) :
    logger.info(f"Verifying OTP for admin with email {verify_admin_schema.email}")
    return await admin_service.verify_otp_forget_password(verify_admin_schema)

@admin_router.put(
    "/ForgetPassword",
    status_code=status.HTTP_200_OK)
async def forget_password(
        admin_data: ForgetPasswordSchema,
        admin_service: Annotated[AdminService, Depends()]
):
    logger.info(f'🔃 Changing admin password for admin {admin_data.email}')
    return await admin_service.change_admin_password(admin_data.email, dict(admin_data))   




@admin_router.get("/Me", response_model=AdminResponseSchema, status_code=status.HTTP_200_OK)
async def read_me(current_admin: Admin = Depends(get_current_admin)) -> AdminResponseSchema:
    logger.info(f"📥 Getting admin with email {current_admin.email}")
    return current_admin
