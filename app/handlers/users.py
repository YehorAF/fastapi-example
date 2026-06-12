import aiofiles
import bson
import datetime
import jwt
from typing import Annotated, Any
from pymongo.errors import DuplicateKeyError
from OpenSSL import crypto
import os
import uuid
import shutil

from fastapi import APIRouter, Request, Depends, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from cache.crud import cache_user, delete_user_cache
from database.users import (
    get_user as mongo_get_user,
    insert_user as mongo_insert_user,
    update_user as mongo_update_user,
    delete_user as mongo_delete_user,
    remove_friends_from_user as mongo_remove_friends_from_user
)
from schemas.users import (
    PyObjectId,
    UserModel,
    GetMeModel, 
    UpdateUserModel, 
    InsertUserModel,
    AuthUserModel
)
from utils import create_or_clear_dir, check_user_actions
from utils.dependencies import is_authed

users_router = APIRouter(prefix="/api/users")


@users_router.get("/{user_id}", response_model=GetMeModel)
async def get_me_or_user(
    user_id: str,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    my_id = user_cache["user_id"]

    if user_id == "me" or user_id == my_id:
        res = await mongo_get_user(bson.ObjectId(my_id))
    elif bson.ObjectId.is_valid(user_id):
        user_id = bson.ObjectId(user_id)

        if user_cache["status"] == "admin":
            res = await mongo_get_user(user_id)
        else:
            my_id = bson.ObjectId(my_id)

            res = await mongo_get_user(user_id, friend_id=my_id)
            res | {"friends": []}

        
        if not res:
            raise HTTPException(404, "there is not such user")
    else:
        raise HTTPException(400, "user_id is not valid")

    return res


@users_router.put("/{user_id}")
async def update_user(
    user_id: PyObjectId,
    user: UpdateUserModel, 
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id, _ = check_user_actions(user_id, user_cache)
    res = await mongo_update_user(
        user_id=user_id,
        **user.model_dump(exclude=["status"])
    )

    if res.modified_count < 1:
        raise HTTPException(400, "cannot update user")
    
    return JSONResponse({"detail": "user was updated"})


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id, is_me = check_user_actions(user_id, user_cache)
    res = await mongo_delete_user(user_id)

    if res.deleted_count < 1:
        raise HTTPException(400, "can not delete user")
    
    try:
        shutil.rmtree(
            f"{os.getenv('PRJ_DIR')}"
            f"{os.getenv('PUBLIC_DIR')}/users/{user_id}"
        )
    except:
        pass

    if is_me:
        await delete_user_cache(user_cache["token"])

    response = JSONResponse({"detail": "user was successfully deleted"})
    response.delete_cookie("token")
    
    return response


@users_router.post("/me/quit")
async def quit_account(user_cache: Annotated[dict[str, Any], Depends(is_authed)]):
    await delete_user_cache(user_cache["token"])

    response = JSONResponse({"detail": "user token was removed"})
    response.delete_cookie("token")

    return response


# prepare encoding for web
@users_router.post("/me/sign")
async def sign_user(request: Request, user: InsertUserModel):
    # try:
    #     password = jwt.decode(
    #         user.password, 
    #         os.getenv("PUB_KEY"),
    #         "RS256"
    #     )["password"]
    # except KeyError:
    #     raise HTTPException(400, "Incorrect password encoding")
    # except:
    #     raise HTTPException(400, "Can not decode hashed password")

    pk = crypto.PKey()
    pk.generate_key(crypto.TYPE_RSA, 512)
    salt = crypto.dump_privatekey(crypto.FILETYPE_PEM, pk)
    password = jwt.encode({"password": user.password}, salt, algorithm="RS256")

    try:
        res = await mongo_insert_user(
            **user.model_dump(exclude=["password"]), salt=salt, password=password)
        inserted_id = str(res.inserted_id)
    except DuplicateKeyError as err:
        raise HTTPException(
            400, 
            "Account with such email or username have already created"
        )
    except Exception as err:
        raise HTTPException(400, str(err)) # add information

    token = uuid.uuid4().hex
    exp_time = int(os.getenv("EXP_TIME")) or 2592000

    await cache_user(
        request.client.host, inserted_id, token, "user", exp_time
    )

    response = JSONResponse(content={}, headers={"X-UserId": inserted_id})
    response.set_cookie(
        "token", 
        token, 
        exp_time, 
        # datetime.datetime.now() + datetime.timedelta(seconds=exp_time)
    )

    return response


@users_router.post("/me/auth")
async def auth_user(request: Request, user: AuthUserModel):
    # try:
    #     password = jwt.decode(
    #         user.password, 
    #         os.getenv("PUB_KEY"),
    #         "RS256"
    #     )["password"]
    # except KeyError:
    #     raise HTTPException(400, "Incorrect password encoding")
    # except:
    #     raise HTTPException(400, "Can not decode hashed password")
    
    res = await mongo_get_user(
        email=user.email, fields={"password": 1, "salt": 1, "status": 1})
    
    if not res:
        raise HTTPException(
            status_code=400, 
            detail="Password is not valid or user doesn't exist"
        )
    
    check_password = jwt.encode(
        {"password": user.password}, res["salt"], "RS256")
    
    if check_password != res["password"]:
        raise HTTPException(
            status_code=400, 
            detail="Password is not valid or user doesn't exist"
        )
    
    user_id = str(res["_id"])
    status = res["status"]
    token = uuid.uuid4().hex
    exp_time = int(os.getenv("EXP_TIME")) or 2592000

    await cache_user(request.client.host, user_id, token, status, exp_time)

    response = JSONResponse(content={}, headers={"X-UserId": user_id})
    response.set_cookie(
        "token", 
        token, 
        exp_time, 
        # datetime.datetime.now() + datetime.timedelta(seconds=exp_time)
    )

    return response


@users_router.delete("/me/friends/{friend_id}")
async def remove_friend(
    friend_id: str,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    friend_id = bson.ObjectId(friend_id)
    user_id = bson.ObjectId(user_cache["user_id"])

    res = await mongo_remove_friends_from_user(user_id, friend_id)

    if res.modified_count < 2:
        raise HTTPException(400, "users were updated but affected only one record")
    
    return JSONResponse({"detail": "friend was successfully removed"})


@users_router.post("/me/photo/upload")
async def upload_photo(
    file: UploadFile,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    dir_uri = f"{os.getenv('PUBLIC_DIR')}/users/{user_id}"
    photo_uri = f"{dir_uri}/{user_id}-{file.filename}"

    create_or_clear_dir(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

    async with aiofiles.open(f"{os.getenv('PRJ_DIR')}/{photo_uri}", "wb") as fp:
        while True:
            if (data := await file.read(int(os.getenv("FILE_SIZE")) or 1024)):
               await fp.write(data)
            else:
                break

    res = await mongo_update_user(user_id, photo=photo_uri)

    if res.modified_count < 1:
        shutil.rmtree(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

        raise HTTPException(400, "user was not updated with photo")
    
    return JSONResponse({"detail": "photo was uploaded"})