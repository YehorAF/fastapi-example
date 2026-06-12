import aiofiles
import bson
from typing import Annotated, Any
import os
import shutil

from fastapi import APIRouter, Query, Depends, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from database.days import (
    get_day_with_checking as mongo_get_day_with_checking,
    get_day_list_with_checking as mongo_get_day_list_with_checking,
    insert_day as mongo_insert_day,
    update_day as mongo_update_day,
    delete_day as mongo_delete_day
) 
from database.users import get_user as mongo_get_user
from schemas import PyObjectId
from schemas.days import (
    DayModel,
    GetDayModel,
    GetDayListModel
)
from schemas.queries import QueryDays
from utils import create_or_clear_dir
from utils.dependencies import is_authed

days_router = APIRouter(prefix="/api/days")


@days_router.get("/", response_model=GetDayListModel)
async def get_day_list(
    query: Annotated[QueryDays, Query()],
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    res = await mongo_get_day_list_with_checking(
        bson.ObjectId(user_cache["user_id"]),
        **query.model_dump()
    )

    return {"days": res}


@days_router.post("/")
async def add_day(
    day: DayModel,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user = await mongo_get_user(bson.ObjectId(user_cache["user_id"]))
    res = await mongo_insert_day(
        user_id=user["_id"],
        username=user["username"],
        email=user["email"],
        user_photo=user["photo"],
        **day.model_dump(by_alias=True, exclude_none=True)
    )

    day_id = res.inserted_id
    if not day_id:
        raise HTTPException(400, "cannot insert day")

    return JSONResponse({"detail": "day was inserted", "day_id": str(day_id)})


@days_router.post("/{day_id}/photo/upload")
async def upload_photo(
    day_id: PyObjectId,
    file: UploadFile,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    dir_uri = f"{os.getenv('PUBLIC_DIR')}/days/{day_id}"
    photo_uri = f"{dir_uri}/{day_id}-{file.filename}"

    create_or_clear_dir(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

    async with aiofiles.open(f"{os.getenv('PRJ_DIR')}/{photo_uri}", "wb") as fp:
        while True:
            if (data := await file.read(int(os.getenv("FILE_SIZE")) or 1024)):
               await fp.write(data)
            else:
                break

    res = await mongo_update_day(
        bson.ObjectId(day_id), user_id, photo=photo_uri)

    if res.modified_count < 1:
        shutil.rmtree(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

        raise HTTPException(400, "day was not updated with photo")
    
    return JSONResponse({"detail": "photo was uploaded"})


@days_router.get("/{day_id}", response_model=GetDayModel)
async def get_day(
    day_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    res = await mongo_get_day_with_checking(
        bson.ObjectId(user_cache["user_id"]),
        bson.ObjectId(day_id)
    )

    if not res:
        raise HTTPException(404, "there is not such day")
    
    return res


@days_router.put("/{day_id}")
async def update_day(
    day_id: PyObjectId,
    day: DayModel,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    res = await mongo_update_day(
        _id=bson.ObjectId(day_id),
        user_id=bson.ObjectId(user_cache["user_id"]),
        **day.model_dump(include=["reaction", "description"], by_alias=True)
    )

    if res.modified_count < 1:
        raise HTTPException(400, "cannot update day")
    
    return JSONResponse({"detail": "day was updated"})


@days_router.delete("/{day_id}")
async def delete_day(
    day_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    res = await mongo_delete_day(
        bson.ObjectId(day_id),
        bson.ObjectId(user_cache["user_id"])
    )

    if res.deleted_count < 1:
        raise HTTPException(400, "cannot delete day")
    
    try:
        shutil.rmtree(
            f"{os.getenv('PRJ_DIR')}"
            f"{os.getenv('PUBLIC_DIR')}/days/{day_id}"
        )
    except:
        pass
    
    return JSONResponse({"detail": "day was deleted"})