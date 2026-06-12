from bson import ObjectId
from pathlib import Path
import os

from fastapi.exceptions import HTTPException

from schemas import PyObjectId


def create_or_clear_dir(dir_uri: str):
    if not Path(dir_uri).exists():
        os.mkdir(dir_uri)
    else:
        for f in os.listdir(dir_uri):
            os.remove(f"{dir_uri}/{f}")


def check_user_actions(
    user_id: PyObjectId, 
    user_cache: dict
) -> tuple[ObjectId, bool]:
    my_id = ObjectId(user_cache["user_id"])
    is_me = False

    if user_id == "me" or user_id == my_id:
        user_id = ObjectId(user_cache["user_id"])
        is_me = True
    elif user_cache["status"] == "admin" and ObjectId.is_valid(user_id):
        user_id = ObjectId(user_id)
    else:
        raise HTTPException(
            400, 
            "user_id is not valid or you haven't permission for this action"
        )
    
    return user_id, is_me