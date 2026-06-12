import bson
from datetime import datetime
from typing import Literal, Any
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from database import mongodb, filter_options
from schemas import RequestStatusEnum


async def get_request(
    _id: bson.ObjectId = None, 
    from_user_id: bson.ObjectId = None,
    to_user_email: bson.ObjectId = None,
    status: RequestStatusEnum = None,
    min_timestamp: datetime = None,
    max_timestamp: datetime = None,
    *args, **kwargs
):
    return await mongodb.requests.find_one(filter_options({
        "_id": _id,
        "from_use._id": from_user_id,
        "to": to_user_email,
        "status": status,
        "timestamp": filter_options(
            {"$gte": min_timestamp, "$lte": max_timestamp}
        )
    }))


async def get_request_list(
    from_user_id: bson.ObjectId = None,
    to_user_email: str = None,
    to_user_id: bson.ObjectId = None,
    status: RequestStatusEnum = None,
    min_timestamp: datetime = None,
    max_timestamp: datetime = None ,
    *args, **kwargs  
):
    return await mongodb.requests.find(filter_options({
        "from_user._id": from_user_id,
        "to.email": to_user_email,
        "to._id": to_user_id,
        "status": status,
        "timestamp": filter_options(
            {"$gte": min_timestamp, "$lte": max_timestamp}
        )
    })).to_list()


async def get_request_list_with_checking(
    my_id: bson.ObjectId = None,
    my_email: str = None,
    user_id: bson.ObjectId = None,
    user_email: str = None,
    query_type: Literal["me", "my"] = "me",
    *args, **kwargs
) -> list[dict[str, Any]] | None:
    if query_type == "me":
        filtered_options = filter_options({
            "to.email": my_email, 
            "to._id": my_id, 
            "from_user._id": user_id,
            "from_user.email": user_email
        })
    elif query_type == "my":
        filtered_options = filter_options({
            "to.email": user_email, 
            "to._id": user_id, 
            "from_user._id": my_id,
            "from_user.email": my_email
        })
    
    return await mongodb.requests.find(filtered_options).to_list()


async def insert_request(
    to_user_email: str,
    from_user_id: bson.ObjectId,
    from_user_username: str,
    from_user_email: str,
    from_user_photo: str  = None,
    to_user_id: bson.ObjectId = None,
    status: RequestStatusEnum = "waiting",
    *args, **kwargs
):
    return await mongodb.requests.insert_one({
        "from_user": {
            "_id": from_user_id,
            "username": from_user_username,
            "email": from_user_email,
            "photo": from_user_photo
        },
        "to": {
            "_id": to_user_id,
            "email": to_user_email
        },
        "status": status,
        "timestamp": datetime.now()
    })


async def insert_request_with_cheking(
    to_user_email: str,
    from_user_id: bson.ObjectId,
    from_user_username: str,
    from_user_email: str,
    from_user_photo: str  = None,
    to_user_id: bson.ObjectId = None,
    status: RequestStatusEnum = "waiting",
    *args, **kwargs
):
    res = await mongodb.requests.find({"$or":[
        {
            "from_user._id": from_user_id,
            "to._id": to_user_id
        },
        {
            "from_user._id": to_user_id,
            "to._id": from_user_id
        }
    ]}).to_list()

    if res:
        raise DuplicateKeyError("you already have request")

    return await insert_request(
        to_user_email=to_user_email,
        from_user_id=from_user_id,
        from_user_username=from_user_username,
        from_user_email=from_user_email,
        from_user_photo=from_user_photo,
        to_user_id=to_user_id,
        status=status,
        *args, **kwargs
    )


async def update_request(
    _id: bson.ObjectId, 
    reciever_id: bson.ObjectId,
    status: RequestStatusEnum
):
    return await mongodb.requests.update_one(
        {"_id": _id, "to._id": reciever_id}, 
        {"$set": {"status": status}}
    )


async def find_and_update_request(
    request_id: bson.ObjectId,
    reciever_id: bson.ObjectId,
    status: RequestStatusEnum,
    *args, **kwargs
):  
    return await mongodb.requests.find_one_and_update(
        {"_id": request_id, "to._id": reciever_id},
        {"$set": {"status": status}},
        return_document=ReturnDocument.AFTER
    )


async def find_and_delete_request(
    request_id: bson.ObjectId,
    reciever_id: bson.ObjectId,
    *args, **kwargs
):
    return await mongodb.requests.find_one_and_delete(
        {"_id": request_id, "to._id": reciever_id}
    )