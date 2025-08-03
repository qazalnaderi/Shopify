from bson import ObjectId
from fastapi import Depends, UploadFile, HTTPException, status
from loguru import logger
from typing import Annotated, Generator, Callable, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorGridOut
from domain.models.media_model import MediaGridFSModel
from domain.schemas.media_schema import MediaSchema
from infrastructure.repositories.media_repository import MediaRepository
from infrastructure.storage.gridfs_storage import GridFsStorage


class MediaService:
    def __init__(
        self,
        media_repository: Annotated[MediaRepository, Depends()],
        storage: Annotated[GridFsStorage, Depends()],
    ):
        self.media_repository = media_repository
        self.storage = storage

    async def create_media(self, file: UploadFile, user_id: str) -> MediaSchema:
        storage_id = await self.storage.save_file(file)
        media = MediaGridFSModel(
            storage_id=storage_id,
            filename=file.filename,
            content_type=file.content_type,
            size=file.size,
            user_id=user_id,
        )
        await self.media_repository.create_media(media)
        logger.info(f"Media {media.filename} created")
        return MediaSchema(
            mongo_id=str(media.mongo_id),
            filename=media.filename,
            content_type=media.content_type,
            size=media.size,
            upload_date=media.upload_date,
            user_id=media.user_id,
            message="Media uploaded successfully",
        )

    async def __get_media_model(self, media_id: ObjectId, user_id: str) -> Tuple[MediaGridFSModel, AsyncIOMotorGridOut]:
        media = await self.media_repository.get_media(media_id)
        # if not media:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Media not found"
        #     )
        if media.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this media",
            )
        file = await self.storage.get_file(media.storage_id)

        logger.info(f"Media {media.filename} retrieved")

        return media, file
    
    async def get_public_media(
    self, media_id: ObjectId
    ) -> tuple[MediaSchema, Callable[[], Generator[Any, Any, None]]]:
        media = await self.media_repository.get_media(media_id)
        logger.info(f"media found: {media}")

        if not media:
            # raise HTTPException(status_code=404, detail="Media not found")
            logger.info(f"media was not found idk whyyyyyyyyyy")
            return []
        logger.info(f"storage_id: {media.storage_id}")    

        file = await self.storage.get_file(media.storage_id)

        def file_stream():
            yield file

        logger.info(f"[Public] Retrieving media file {media.filename}")
        return (
            MediaSchema(
                mongo_id=media.mongo_id,
                filename=media.filename,
                content_type=media.content_type,
                size=media.size,
                upload_date=media.upload_date,
                user_id=media.user_id,
                message="Public media downloaded successfully",
            ),
            file_stream,
        )


    async def get_media(
        self, media_id: ObjectId, user_id: str
    ) -> tuple[MediaSchema, Callable[[], Generator[Any, Any, None]]]:
        media, file = await self.__get_media_model(media_id, user_id)

        def file_stream():
            yield file

        logger.info(f"Retrieving media file {media.filename}")
        return (
            MediaSchema(
                mongo_id=media.mongo_id,
                filename=media.filename,
                content_type=media.content_type,
                size=media.size,
                upload_date=media.upload_date,
                user_id=media.user_id,
                message="Media downloaded successfully",
            ),
            file_stream,
        )

    async def get_media_data(self, media_id: str, user_id: str) -> bytes:
        _, file = await self.__get_media_model(ObjectId(media_id), user_id)
        logger.info(f"Retrieving media file {media_id}")
        return file
