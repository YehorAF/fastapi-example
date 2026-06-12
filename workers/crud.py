from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne, UpdateMany
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]


def remove_requests():
    return db.requests.delete_many({
        "timestamp": {
            "$lt": datetime.now() - 
            timedelta(seconds=int(os.getenv("EXP_TIME")))
        }
    })


def remove_orphaned_days():
    res = [v["_id"] for v in db.days.aggregate([
        {
            "$lookup": {
                "from": "users",
                "localField": "user._id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$match": {"user": {"$size": 0}}},
        {"$project": {"_id": 1}}
    ])]

    if res:
        max_del = int(os.getenv("MAX_DEL", 20))
        for i in range(0, len(res), max_del):
            db.days.delete_many({"_id": {"$in": res[i:i+max_del]}})


def update_user_references():
    friend_batches = []
    request_batches = []
    day_batches = []

    max_del = int(os.getenv("MAX_DEL", 20))
    i = 0
    for res in db.users.find({}, {"email": 1, "username": 1, "photo": 1}):
        friend_batches.append(UpdateMany(
            {"friends._id": res["_id"]},
            {"$set": {
                "friends.$.email": res["email"],
                "friends.$.username": res["username"],
                "friends.$.photo": res["photo"],
            }}
        ))
        request_batches.append(UpdateMany(
            {"from_user._id": res["_id"]},
            {"$set": {
                "from_user.email": res["email"],
                "from_user.username": res["username"],
                "from_user.photo": res["photo"],
            }}
        ))
        day_batches.append(UpdateMany(
            {"user._id": res["_id"]},
            {"$set": { 
                "user.email": res["email"],
                "user.username": res["username"],
                "user.photo": res["photo"],
            }}
        ))

        if i and i % (max_del - 1) == 0:
            db.users.bulk_write(friend_batches)
            db.requests.bulk_write(request_batches)
            db.days.bulk_write(day_batches)

            friend_batches = []            
            request_batches = []
            day_batches = []

        i += 1

    if friend_batches:
        db.users.bulk_write(friend_batches)
        db.requests.bulk_write(request_batches)
        db.days.bulk_write(day_batches)


def remove_orphaned_friends():
    res = db.users.aggregate([
        { "$unwind": "$friends" },
        {
            "$lookup": {
                "from": "users",
                "localField": "friends._id",
                "foreignField": "_id",
                "as": "main_user"
            }
        },
        {"$match": {"main_user": {"$size": 0}}},
        {"$project": {"friends._id": 1}},
        {
            "$group": {
                "_id": "$_id", 
                "orphaned_friends": {
                    "$push": "$friends._id"
                }
            }
        }
    ]).to_list()

    if res:
        max_del = int(os.getenv("MAX_DEL", 20))
        batches = []
        for i in range(0, len(res)):
            batches.append(UpdateOne(
                {"_id": res[i]["_id"]},
                {
                    "$pull": {
                        "friends": {
                            "_id": {"$in": res[i]["orphaned_friends"]}
                        }
                    }
                }
            ))
            if i and i % (max_del - 1) == 0:
                db.users.bulk_write(batches)
                batches = []

        if batches:
            db.users.bulk_write(batches)