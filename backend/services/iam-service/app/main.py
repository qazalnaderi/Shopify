import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
import os
import uvicorn
from multiprocessing import Process
logger = logging.getLogger(__name__)
logger.info("Custom logging is configured.")
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.v1.endpoints.user_route import user_router
from api.v1.endpoints.buyer_route import buyer_router
from api.v1.endpoints.admin_route import admin_router
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.info("IAM Service Started")

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(buyer_router, prefix="/api/v1/buyers", tags=["buyers"])
app.include_router(admin_router, prefix="/api/v1/admins", tags=["admins"])

@app.get("/")
async def root():
    return {"message": "Hello Dear! Welcome to the IAM service."}

def run_iam():

    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    p1 = Process(target=run_iam)


    p1.start()

    p1.join()

