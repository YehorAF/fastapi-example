import bson
from typing import Literal, Any
from pymongo import UpdateOne

from database import mongodb, filter_options


async def get_user(
    user_id: bson.ObjectId = None,
    email: str = None,
    username: str = None,
    friend_id: bson.ObjectId = None,
    friend_email: str = None,
    fields = {"password": 0, "salt": 0},
    *args, **kwargs
):
    return await mongodb.users.find_one(
        filter_options({
            "_id": user_id,
            "username": username,
            "email": email,
            "friends._id": friend_id,
            "friends.email": friend_email,
        }), 
        fields
    )


async def get_user_list(
    ids: list[bson.ObjectId] = None,
    usernames: list[bson.ObjectId] = None,
    emails: list[bson.ObjectId] = None,
    sort: Literal[-1, 1] = 1,
    sort_by: str = "_id",
    skip: int = 0,
    limit: int = None,
    is_or: bool = False,
    fields={},
    *args, **kwargs
):
    filtered_options = filter_options({
        "_id": {"$in": ids} if ids else None,
        "username": {"$in": usernames} if usernames else None,
        "email": {"$in": emails} if emails else None,
    })

    if is_or:
        filtered_options = {
            "$or": [{k: v} for k, v in filtered_options.items()]
        }

    return await mongodb.users.find(
        filtered_options,
        {"password": 0, "salt": 0} | fields
    ).sort(sort_by, sort).skip(skip).to_list(limit)


async def insert_user(
    email: str,
    username: str,
    photo: str,
    salt: str,
    password: str,
    status: Literal["user", "admin"] = "user",
    *args, **kwargs
):
    return await mongodb.users.insert_one({
        "email": email,
        "username": username,
        "photo": photo,
        "salt": salt,
        "password": password,
        "status": status,
        "friends": []
    })


async def update_user(
    user_id: bson.ObjectId,
    email: str = None,
    password: str = None,
    photo: str = None,
    status: Literal["user", "admin"] = None,
    *args, **kwargs
):
    return await mongodb.users.update_one(
        {"_id": user_id},
        {"$set": filter_options({
            "email": email,
            "password": password,
            "photo": photo,
            "status": status
        })}
    )


async def add_friends_to_users(user1: dict[str, Any], user2: dict[str, Any]):
    return await mongodb.users.bulk_write([
        UpdateOne({"_id": user1["_id"]}, {"$push": {"friends": user2}}),
        UpdateOne({"_id": user2["_id"]}, {"$push": {"friends": user1}}),
    ])


async def remove_friends_from_user(
    user1_id: bson.ObjectId, 
    user2_id: bson.ObjectId
):
    return await mongodb.users.bulk_write([
        UpdateOne({"_id": user1_id}, {"$pull": {"friends": {"_id": user2_id}}}),
        UpdateOne({"_id": user2_id}, {"$pull": {"friends": {"_id": user1_id}}})
    ])


async def delete_user(user_id: bson.ObjectId):
    return await mongodb.users.delete_one({"_id": user_id})