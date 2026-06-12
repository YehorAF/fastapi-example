import bson
from datetime import datetime
from typing import Literal

from database import mongodb, filter_options
from database.users import get_user
from schemas import ReactionEnum


async def get_day(
    user_id: bson.ObjectId = None,
    day_id: bson.ObjectId = None,
    reaction: ReactionEnum = None,
) -> dict | None:
    return await mongodb.days.find_one(filter_options({
        "user._id": user_id,
        "day_id": day_id,
        "reaction": reaction,
    }))


async def get_day_with_checking(
    my_id: bson.ObjectId,
    day_id: bson.ObjectId,
):
    if not (res := await mongodb.days.find_one({"_id": day_id})):
        return

    if (user_id := res["user"]["_id"]) == my_id:
        return res
    
    if await mongodb.users.find_one({"_id": user_id, "friends._id": my_id}):
        return res


async def get_day_list(
    user_id: bson.ObjectId = None,
    ids: list[bson.ObjectId] = None,
    user_ids: list[bson.ObjectId] = None,
    reactions: list[ReactionEnum] = None,
    min_timestamp: datetime = None,
    max_timestamp: datetime = None,
    limit: int = None,
    skip: int = 0,
    sort: Literal[-1, 1] = 1,
    sort_by: str = "_id",
    is_my: bool = False,
    *args, **kwargs
) -> list[dict]:
    if is_my:
        user_ids_filter = user_id
    else:
        user_ids_filter = {"$in": user_ids} if user_ids else None

    filtered_options = filter_options({
            "_id": {"$in": ids} if ids else None,
            "user._id": user_ids_filter,
            "reaction": {"$in": reactions} if reactions else None,
            "created": filter_options({
                "$gte": min_timestamp,
                "$lte": max_timestamp
            }) or None
        })

    return await mongodb.days.find(filtered_options)\
        .sort(sort_by, sort).skip(skip).to_list(limit)


async def get_day_list_with_checking(
    user_id: bson.ObjectId,
    ids: list[bson.ObjectId] = None,
    user_ids: list[bson.ObjectId] = None,
    reactions: list[ReactionEnum] = None,
    min_timestamp: datetime = None,
    max_timestamp: datetime = None,
    limit: int = None,
    skip: int = 0,
    sort: Literal[-1, 1] = 1,
    sort_by: str = "_id",
    is_my: bool = False,
    *args, **kwargs
):
    user_ids_set = None

    if not is_my:
        user = await get_user(user_id=user_id)
        friends = user.get("friends") or []

        if not friends:
            return []
        
        friends = [friend["_id"] for friend in friends]

        if user_ids:
            user_ids_set = list(set(user_ids or []).intersection(friends))
        else: 
            user_ids_set = friends
    
    return await get_day_list(
        user_id=user_id,
        ids=ids,
        user_ids=user_ids_set,
        reactions = reactions,
        min_timestamp = min_timestamp,
        max_timestamp = max_timestamp,
        limit = limit,
        skip = skip,
        sort = sort,
        sort_by = sort_by,
        is_my=is_my
    )


async def insert_day(
    reaction: ReactionEnum,
    description: str,
    user_id: str,
    username: str,
    email: str,
    user_photo: str,
    photo: str | None = None,
):
    return await mongodb.days.insert_one({
        "reaction": reaction,
        "description": description,
        "photo": photo,
        "created": datetime.now(),
        "user": {
            "_id": user_id,
            "username": username,
            "email": email,
            "photo": user_photo,
        }
    })


async def update_day(
    _id: bson.ObjectId,
    user_id: bson.ObjectId,
    reaction: ReactionEnum = None,
    description: str = None,
    photo: str = None,
):
    return await mongodb.days.update_one(
        {"_id": _id, "user._id": user_id},
        {"$set": filter_options({
            "reaction": reaction,
            "description": description,
            "photo": photo,
            "last_updated": datetime.now()
        })}
    )


async def delete_day(_id: bson.ObjectId, user_id: bson.ObjectId):
    return await mongodb.days.delete_one({"_id": _id, "user._id": user_id})