import bson
from pymongo.errors import DuplicateKeyError
from typing import Annotated, Any

from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from database.users import (
    get_user_list as mongo_get_user_list,
    add_friends_to_users as mongo_add_friends_to_users
    
)
from database.requests import (
    get_request_list as mongo_get_request_list,
    insert_request_with_cheking as mongo_insert_request_with_cheking,
    update_request as mongo_update_request,
    find_and_update_request as monogo_find_and_update_request,
    find_and_delete_request as mongo_find_and_delete_request
)
from schemas import PyObjectId
from schemas.requests import InsertRequestModel, GetRequestListModel
from schemas.queries import QueryRequests
from utils.dependencies import is_authed

requests_router = APIRouter(prefix="/api/requests")


@requests_router.get("/", response_model=GetRequestListModel)
async def get_request_list(
    query: Annotated[QueryRequests, Query()],
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    if query.query_type == "my":
        options = {"from_user_id": user_id}
    else:
        options = {"to_user_id": user_id}

    res = await mongo_get_request_list(**options, **query.model_dump())
    return {"requests": res}


@requests_router.post("/")
async def send_request(
    friend_request: InsertRequestModel,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    reciever_email = friend_request.to.email
    users = await mongo_get_user_list(
        ids=[user_id], emails=[reciever_email], is_or=True
    )

    if len(users) < 2:
        raise HTTPException(404, "there are not user with such email")
    
    sender = list(filter(lambda v: v["_id"] == user_id, users))[0]

    if users[0]["_id"] == user_id and users[1]["email"] == reciever_email:
        sender = users[0]
        reciver = users[1]
    elif users[0]["email"] == reciever_email and users[1]["_id"] == user_id:
        sender = users[1]
        reciver = users[0]
    else:
        raise HTTPException(404, "there are not user with such email and id")

    try:
        res = await mongo_insert_request_with_cheking(
            to_user_email=friend_request.to.email,
            to_user_id=reciver["_id"],
            from_user_id=user_id,
            from_user_username=sender["username"],
            from_user_email=sender["email"],
            from_user_photo=sender["photo"],
        )
    except DuplicateKeyError:
        raise HTTPException(400, "you or your friend sent request")

    if not res.inserted_id:
        raise HTTPException(400, "cannot send request")
    
    return JSONResponse({"detail": "request was sent"})


@requests_router.post("/{request_id}/approve")
async def approve_request(
    request_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    # res = await monogo_find_and_update_request(
    #     bson.ObjectId(request_id), user_id, "approved"
    # )

    res = await mongo_find_and_delete_request(bson.ObjectId(request_id), user_id)

    if not res:
        raise HTTPException("No such request")
    
    users = await mongo_get_user_list(
        [user_id, res["from_user"]["_id"]], 
        fields={"friends": 0}
    )

    if len(users) < 2:
        raise HTTPException(404, "user, who sent you request, doesn't exist")
    elif len(users) > 2:
        raise HTTPException(
            500, 
            "there are more than two request members. somethong go wrong"
        )

    if users[1]["_id"] == user_id:
        users.reverse()
    
    reciever, sender = tuple(users)
    res = await mongo_add_friends_to_users(reciever, sender)

    if res.modified_count < 2:
        raise HTTPException(400, "can not add friends")

    return JSONResponse({"detail": "request was succesfully approved"})


@requests_router.post("/{request_id}/decline")
async def decline_request(
    request_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    # res = await mongo_update_request(
    #     bson.ObjectId(request_id), user_id, "declined"
    # )
    res = await mongo_find_and_delete_request(bson.ObjectId(request_id), user_id)

    if not res:
        raise HTTPException(400, "can not update request")
    
    return JSONResponse({"detail": "request was succesfully declined"})