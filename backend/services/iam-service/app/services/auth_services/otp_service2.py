import random
from typing import Annotated
from loguru import logger
from fastapi import Depends
from redis import Redis

from services.base_service import BaseService
from domain.models.otp_model import OTP
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from core.postgres_db.database import get_db

# class OTPService(BaseService):
#     def __init__(
#         self, redis_client: Annotated[Redis, Depends(get_redis_client)]
#     ) -> None:
#         super().__init__()
#         self.redis_client = redis_client

#     @staticmethod
#     def __generate_otp() -> str:
#         return str(random.randint(100000, 999999))

#     def send_otp(self, email: str):
#         otp = self.__generate_otp()
#         self.redis_client.setex(email, self.config.OTP_EXPIRE_TIME, otp)
#         logger.info(f"OTP {otp} sent to email {email}")
#         return otp

#     def verify_otp(self, email: str, otp: str) -> bool:
#         stored_otp = self.redis_client.get(email)
#         return stored_otp is not None and stored_otp == otp

#     def check_exist(self, email: str) -> bool:
#         stored_otp = self.redis_client.get(email)
#         return stored_otp is not None



class OTPService(BaseService):
    def __init__(self, db: Annotated[Session, Depends(get_db)]) -> None:
        super().__init__()
        self.db = db

    @staticmethod
    def __generate_otp() -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, email: str):
        otp = self.__generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.config.OTP_EXPIRE_TIME)

        new_otp = OTP(email=email, otp=otp, expires_at=expires_at)
        self.db.add(new_otp)
        self.db.commit()

        logger.info(f"OTP {otp} sent to email {email}")
        return otp

    def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = self.db.query(OTP).filter(OTP.email == email).order_by(OTP.created_at.desc()).first()

        if stored_otp.expires_at.tzinfo is None:
            stored_otp.expires_at = stored_otp.expires_at.replace(tzinfo=timezone.utc)

        if str(stored_otp.otp) == otp and  stored_otp.expires_at > datetime.now(timezone.utc):
            return True
        return False

    def check_exist(self, email: str) -> bool:
        stored_otp = self.db.query(OTP).filter(OTP.email == email).order_by(OTP.created_at.desc()).first()
        expires_at = stored_otp.created_at + timedelta(minutes=self.config.OTP_EXPIRE_TIME)
        logger.info(f"expire: {stored_otp.expires_at} and expires:{expires_at}")

        if stored_otp and expires_at > datetime.now(timezone.utc):
            return stored_otp
        return None