import random
import requests
from loguru import logger
from redis import Redis
from datetime import timedelta
from core.redis.redis_client import get_redis_client
from typing import Annotated
from loguru import logger
from fastapi import Depends
from redis import Redis
import random
import requests
from loguru import logger
from redis import Redis
from datetime import timedelta
from core.redis.redis_client import get_redis_client
from typing import Annotated
from fastapi import Depends

class OTPService:
    def __init__(self, redis_client: Annotated[Redis, Depends(get_redis_client)]) -> None:
        self.public_key = "m6wF54HaYmHYIqqZx"  # Public Key که همون User ID هست
        self.service_id = "service_w1woy8l"  # Service ID از داشبورد EmailJS
        self.template_id = "template_i6ygg4f"  # Template ID از داشبورد EmailJS
        self.redis_client = redis_client  # Redis client برای ذخیره OTP

    @staticmethod
    def __generate_otp() -> str:
        return str(random.randint(100000, 999999))

    def send_otp(self, email: str):
        otp = self.__generate_otp()

        # ارسال درخواست به EmailJS برای ارسال OTP
        url = "https://api.emailjs.com/api/v1.0/email/send"
        data = {
            "service_id": self.service_id,
            "template_id": self.template_id,
            "user_id": self.public_key,  # استفاده از Public Key به جای User ID
            "template_params": {
                "otp": otp,  # کد OTP که به صورت داینامیک در ایمیل قرار می‌گیره
                "to_email": email  # ایمیل گیرنده
            }
        }

        # ارسال درخواست POST به EmailJS API
        response = requests.post(url, json=data)

        if response.status_code == 200:
            logger.info(f"OTP {otp} sent to email {email}")
            # ذخیره OTP در Redis با زمان انقضای 5 دقیقه
            self.redis_client.setex(email, timedelta(minutes=5), otp)
        else:
            logger.error(f"Failed to send OTP: {response.status_code} - {response.text}")

        return otp

    def verify_otp(self, email: str, otp: str) -> bool:
        # بررسی OTP ذخیره شده در Redis
        stored_otp = self.redis_client.get(email)
        
        if stored_otp is None:
            logger.error(f"No OTP found for email {email}. It might have expired.")
            return False
        
        if stored_otp.decode('utf-8') == otp:
            logger.info(f"OTP for email {email} verified successfully.")
            return True
        else:
            logger.error(f"Failed to verify OTP for email {email}.")
            return False

    def check_exist(self, email: str) -> bool:
        # بررسی اینکه آیا OTP قبلاً برای این ایمیل ارسال شده است یا خیر
        stored_otp = self.redis_client.get(email)
        return stored_otp is not None
