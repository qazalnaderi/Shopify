from uuid import UUID
from fastapi import APIRouter, Depends, status, Request
from loguru import logger
from domain.schemas.bind_schema import ItemImageBasicSchema
from services.item_image_main_service import ItemImageMainService
from services.auth_service import get_current_user
from uuid import UUID
from validator.validator import validate_image_file
from typing import Annotated, List
from domain.schemas.token_schema import TokenDataSchema
from services.media_service import MediaService
from fastapi import APIRouter, Depends, UploadFile, status, Form, HTTPException, File
from fastapi.responses import StreamingResponse
from bson import ObjectId
from validator.validator import validate_image_file
item_media_router = APIRouter()

@item_media_router.post("/upload_item_images/{item_id}", status_code=status.HTTP_201_CREATED)
async def upload_item_images(
    item_id: UUID,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    media_service: Annotated[MediaService, Depends()],
    item_image_service: Annotated[ItemImageMainService, Depends()],
    files: List[UploadFile] = File(...),
    is_main_flags: List[str] = Form(...),

):
    logger.info(f"Validating banner file")
    for file in files:
        validate_image_file(file)

    logger.info(f"Uploading banner for item {item_id} {file.filename}")
    if len(is_main_flags) == 1 and "," in is_main_flags[0]:
        is_main_flags = is_main_flags[0].split(",")

    print(len(files), len(is_main_flags))

    if len(files) != len(is_main_flags):
        raise HTTPException(status_code=400, detail="Files and flags count mismatch")

    parsed_flags = [flag.lower() == "true" for flag in is_main_flags]

    if any(parsed_flags):
        await item_image_service.clear_main(item_id)

    for file, is_main in zip(files, parsed_flags):
        output = await media_service.create_media(file, str(current_user.user_id))

        await item_image_service.create(
            item_id=item_id,
            image_url=str(output.mongo_id), 
            is_main=is_main
        )

    return {"message": "Images uploaded and bound to item successfully ✅"}



@item_media_router.get(
    "/get_item_images/{item_id}",
    response_model=List[ItemImageBasicSchema],
    status_code=status.HTTP_200_OK
)
async def get_item_images(
    item_id: UUID,
    item_image_service: Annotated[ItemImageMainService, Depends()]
):
    logger.info(f"Getting all image IDs for item: {item_id}")
    images = await item_image_service.get_all_images(item_id)
    return [
        ItemImageBasicSchema(image_id=image.image_id, is_main=image.is_main)
        for image in images
    ]



@item_media_router.get(
    "/get_item_image/{image_id}",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK
)
async def get_item_image(
    image_id: UUID,
    item_image_service: Annotated[ItemImageMainService, Depends()],
    media_service: Annotated[MediaService, Depends()]
):
    logger.info(f"Getting item image with id: {image_id}")

    image = await item_image_service.get_image_by_id(image_id)


    mongo_id = ObjectId(image.image_url)
    logger.info(f"Mongo ID for image: {mongo_id}")

    media_schema, file_stream = await media_service.get_public_media(mongo_id)

    logger.info(f"Streaming image file {media_schema.filename}")

    return StreamingResponse(
        content=file_stream(),
        media_type=media_schema.content_type,
        headers={
            "Content-Disposition": f"inline; filename={media_schema.filename}"
        },
    )




@item_media_router.put(
    "/update_main_flag/{image_id}",
    status_code=status.HTTP_200_OK
)
async def update_main_flag(
    image_id: UUID,
    item_image_service: Annotated[ItemImageMainService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],):
    return await item_image_service.set_main(image_id)



@item_media_router.delete(
    "/delete/{image_id}",
    status_code=status.HTTP_200_OK
)
async def update_main_flag(
    image_id: UUID,
    item_image_service: Annotated[ItemImageMainService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    ):
    return await item_image_service.delete(image_id)