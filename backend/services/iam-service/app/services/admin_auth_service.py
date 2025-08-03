from typing import Annotated, Dict
from loguru import logger
from domain.models.admin_model import Admin
from services.base_service import BaseService
from uuid import UUID
from services.admin_service import AdminService
from services.auth_services.auth_service import AuthService
from services.auth_services.otp_service import OTPService
from domain.schemas.admin_schema import VerifyOTPResponseSchema, VerifyOTPSchema, ResendOTPResponseSchema, ResendOTPSchema
from fastapi import Depends, HTTPException, status

class AdminAuthService(BaseService):
    def __init__(
        self,
        admin_service: Annotated[AdminService, Depends()],
        otp_service: Annotated[OTPService, Depends()],
        auth_service: Annotated[AuthService, Depends()],
    ) -> None:
        super().__init__()
        self.admin_service = admin_service
        self.otp_service = otp_service
        self.auth_service = auth_service

    async def verify_admin(
        self, verify_admin_schema: VerifyOTPSchema
    ) -> VerifyOTPResponseSchema:
        if not self.otp_service.verify_otp(
            verify_admin_schema.email, verify_admin_schema.otp
        ):
            logger.error(f"Invalid OTP for email {verify_admin_schema.email}❌")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP❌"
            )

        admin = await self.admin_service.get_admin_by_email(
            verify_admin_schema.email
        )

        # await self.admin_service.update_verified_status(admin.admin_id, {"is_verified": True})

        logger.info(f"admin with email{verify_admin_schema.email} verified✅")
        return VerifyOTPResponseSchema(
            verified=True, message="admin Verified Successfully"
        )

    async def resend_otp(
        self, resend_otp_schema: ResendOTPSchema
    ) -> ResendOTPResponseSchema:
        existing_admin = await self.admin_service.get_admin_by_email(
            resend_otp_schema.email
        )
        if not existing_admin:
            logger.error(f"admin with email {resend_otp_schema.email} does not exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="admin does not exist"
            )

        if self.otp_service.check_exist(resend_otp_schema.email):
            logger.error(f"OTP for email {resend_otp_schema.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="OTP already exists"
            )

        otp = self.otp_service.send_otp(resend_otp_schema.email)

        logger.info(f"OTP resent to email {resend_otp_schema.email}")
        return ResendOTPResponseSchema(
            email=resend_otp_schema.email,
            OTP=otp,
            message="OTP sent to email",
        )   

    async def verify_otp_forget_password(
        self, verify_admin_schema: VerifyOTPSchema
    ) :
        if not self.otp_service.verify_otp(
            verify_admin_schema.email, verify_admin_schema.otp
        ):
            logger.error(f"Invalid OTP for email {verify_admin_schema.email}❌")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP❌"
            )

        admin = await self.admin_service.get_admin_by_email(verify_admin_schema.email)
        await self.admin_service.update_verified_status(admin.admin_id, {"can_reset_password": True})

        logger.info(f"admin with email{verify_admin_schema.email} Requested for password reseting")
        return {"status_code": 200, "message": "OTP Verified Successfully"}
