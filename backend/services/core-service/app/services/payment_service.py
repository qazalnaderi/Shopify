import httpx
from loguru import logger
from uuid import UUID
from decimal import Decimal


class PaymentService:
    def __init__(self):
        self.merchant_id = "123e4567-e89b-12d3-a456-426614174000"  
        self.sandbox_request_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        self.sandbox_verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        self.sandbox_startpay_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def create_order_callback_url(self, website_id:UUID ,order_id: UUID) -> str:
        """
        This method constructs the Callback URL based on the order_id.
        You can modify this URL depending on your server's structure.
        """
        base_url = "http://tradehub.localhost/api/v1/payment/order_payment/callback"
        return f"{base_url}/{order_id}?website_id={website_id}"
    async def request_order_payment(self, website_id:UUID, order_id: UUID, amount: Decimal) -> str:


        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(amount),
            "callback_url": self.create_order_callback_url(website_id, order_id),
            "description": f"پرداخت برای سفارش {order_id}",
            "metadata": {}
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            response = await client.post(self.sandbox_request_url, json=payload)
            data = response.json()
            logger.info(f"Payment request response: {data}")

            if data.get("data") and data["data"].get("authority"):
                authority = data["data"]["authority"]
                payment_url = f"{self.sandbox_startpay_url}{authority}"
                return payment_url
            else:
                raise Exception(f"Payment request failed: {data}")

    async def verify_order_payment(self, amount: float, authority: str) -> bool:

        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount ,
            "authority": authority
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            response = await client.post(self.sandbox_verify_url, json=payload)
            data = response.json()
            logger.info(f"Payment verify response: {data}")

            status = data.get("data", {}).get("code")
            logger.info("status",status)
            if status == 100 or status == 101:
                return True
            else:
                return False
            
    def create_plan_callback_url(self, website_id: UUID, plan_id: UUID) -> str:
        base_url = "https://tradehub-core.liara.run/api/v1/payment/plan_payment/callback"
        return f"{base_url}?website_id={website_id}&plan_id={plan_id}"


    async def request_plan_payment(self,website_id:UUID, plan_id: UUID, amount: Decimal) -> str:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": float(amount) ,
            "callback_url": self.create_plan_callback_url(website_id,plan_id),
            "description": f"پرداخت برای خرید پلن {plan_id}",
            "metadata": {}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.sandbox_request_url, json=payload)
            data = response.json()
            logger.info(f"Plan payment request response: {data}")

            if data.get("data") and data["data"].get("authority"):
                authority = data["data"]["authority"]
                payment_url = f"{self.sandbox_startpay_url}{authority}"
                return payment_url
            else:
                raise Exception(f"Plan payment request failed: {data}")

    async def verify_plan_payment(self, amount: float, authority: str) -> bool:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount ,
            "authority": authority
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.sandbox_verify_url, json=payload)
            data = response.json()
            logger.info(f"Plan payment verify response: {data}")

            status = data.get("data", {}).get("code")
            if status == 100 or status == 101:
                return True
            else:
                return False
