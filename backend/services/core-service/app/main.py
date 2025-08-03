import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)
logger.info("Custom logging is configured.")
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.v1.endpoints.websites_routes import website_router
from api.v1.endpoints.item_routes import item_router
from api.v1.endpoints.order_routes import order_router
from api.v1.endpoints.cart_routes import cart_router
from api.v1.endpoints.payment_routes import payment_router
from api.v1.endpoints.review_routes import review_router
from api.v1.endpoints.qan_routes import qan_router
from api.v1.endpoints.admin_routes import admin_router
from api.v1.endpoints.coupon_routes import coupon_router
from api.v1.endpoints.plan_routes import plan_router
from api.v1.endpoints.slug_routes import slug_router
from api.v1.endpoints.favorite_routes import favorite_router
import os
import uvicorn
from multiprocessing import Process
app = FastAPI()

from utils.scheduler_starter import starter

@app.on_event("startup")
async def start_scheduler():
    starter()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.info("Core Service Started")
app.include_router(website_router, prefix="/api/v1/websites", tags=["websites"])
app.include_router(item_router, prefix="/api/v1/items", tags=["items"])
app.include_router(cart_router, prefix="/api/v1/carts", tags=["carts"])
app.include_router(order_router, prefix="/api/v1/order", tags=["orders"])
app.include_router(payment_router, prefix="/api/v1/payment", tags=["payments"])
app.include_router(review_router, prefix="/api/v1/review", tags=["reviews"])
app.include_router(qan_router, prefix="/api/v1/question", tags=["questions"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admins"])
app.include_router(coupon_router, prefix="/api/v1/coupon", tags=["coupons"])
app.include_router(plan_router, prefix="/api/v1/plan", tags=["plans"])
app.include_router(slug_router, prefix="/api/v1/slug", tags=["slugs"])
app.include_router(favorite_router, prefix="/api/v1/favorite", tags=["favorites"])

@app.get("/")
async def root():
    return {"message": "Hello Dear! Welcome to the Core service."}

def run_core():

    uvicorn.run(app, host="0.0.0.0", port=8002)

if __name__ == "__main__":
    p1 = Process(target=run_core)


    p1.start()

    p1.join()
