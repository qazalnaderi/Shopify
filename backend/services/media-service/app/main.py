from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import logging

from api.v1.endpoints.website_media_routes import media_router
from api.v1.endpoints.item_imag_routes import item_media_router

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(media_router, prefix="/api/v1/website", tags=["website_media"])
app.include_router(item_media_router, prefix="/api/v1/item", tags=["item_media"])

logger.info("Media Service Started")


@app.get("/")
async def root():
    return {"message": "Hello Dear! Welcome to Media Service."}

def run_media():

    uvicorn.run(app, host="0.0.0.0", port=8003)

if __name__ == "__main__":
    p1 = Process(target=run_media)


    p1.start()

    p1.join()
