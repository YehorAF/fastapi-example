from typing import Optional
from pydantic import BaseModel, EmailStr, FilePath, AnyUrl, Field

from schemas import PyObjectId


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: EmailStr
    username: str = Field(min_length=8, max_length=32)
    photo: Optional[FilePath | AnyUrl] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "6a2a646f64f4cf027691d857",
                    "email": "email@gmail.com",
                    "username": "username",
                    "photo": "https://domain.com/long-link.jpg"
                },
                {
                    "email": "email@gmail.com",
                    "username": "username",
                },
            ]
        }
    }


class GetMeModel(UserModel):
    friends: list[UserModel]

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "6a2a646f64f4cf027691d857",
                    "email": "my_account@gmail.com",
                    "username": "my_username",
                    "photo": "https://domain.com/my-profile.jpg",
                    "friends": [
                        {
                            "_id": "7b3b757f75f5df138702e968",
                            "email": "friend_one@gmail.com",
                            "username": "friend_one",
                            "photo": "https://domain.com/friend1.jpg"
                        },
                        {
                            "_id": "8c4c868g86g6eg249813fa79",
                            "email": "friend_two@gmail.com",
                            "username": "friend_two",
                            "photo": None
                        }
                    ]
                }
            ]
        }
    }


class InsertUserModel(UserModel):
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "new_user@gmail.com",
                    "username": "new_player_123",
                    "photo": "https://domain.com/avatar.jpg",
                    "password": "SuperSecurePassword123!"
                }
            ]
        }
    }


class UpdateUserModel(UserModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=8, max_length=32)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "updated_username"
                },
                {
                    "email": "updated_email@gmail.com",
                    "photo": "https://domain.com/new-avatar.jpg"
                }
            ]
        }
    }


class AuthUserModel(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@gmail.com",
                    "password": "MySecretPassword"
                }
            ]
        }
    }


class RequestUserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "7b3b757f75f5df138702e968",
                    "email": "recipient@gmail.com"
                }
            ]
        }
    }