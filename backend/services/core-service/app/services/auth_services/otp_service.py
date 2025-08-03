import random
from typing import Annotated
from loguru import logger
from fastapi import Depends
from redis import Redis

from core.redis.redis_client import get_redis_client
from services.base_service import BaseService


class OTPService(BaseService):
    def __init__(
        self, redis_client: Annotated[Redis, Depends(get_redis_client)]
    ) -> None:
        super().__init__()
        self.redis_client = redis_client

    @staticmethod
    def __generate_otp() -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, email: str):
        otp = self.__generate_otp()
        self.redis_client.setex(email, self.config.OTP_EXPIRE_TIME, otp)
        logger.info(f"OTP {otp} sent to email {email}")
        return otp

    def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = self.redis_client.get(email)
        return stored_otp is not None and stored_otp == otp

    def check_exist(self, email: str) -> bool:
        stored_otp = self.redis_client.get(email)
        return stored_otp is not None