from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from schemas import PyObjectId, RequestStatusEnum
from schemas.users import UserModel, RequestUserModel


class RequestModel(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    from_user: UserModel
    to: RequestUserModel
    status: RequestStatusEnum = "waiting"
    timestamp: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "_id": "6a2a646f64f4cf027691d857",
                    "from_user": {
                        "_id": "6a2a646f64f4cf027691d857",
                        "email": "sender@gmail.com",
                        "username": "sender_username",
                        "photo": "https://domain.com/sender-link.jpg"
                    },
                    "to": {
                        "_id": "7b3b757f75f5df138702e968",
                        "username": "recipient_username",
                        "photo": "https://domain.com/recipient-link.jpg"
                    },
                    "status": "waiting",
                    "timestamp": "2026-06-12T11:51:28.000000"
                }
            ]
        }
    }


class GetRequestListModel(BaseModel):
    requests: list[RequestModel]

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "requests": [
                        {
                            "_id": "6a2a646f64f4cf027691d857",
                            "from_user": {
                                "_id": "6a2a646f64f4cf027691d857",
                                "email": "sender@gmail.com",
                                "username": "sender_username",
                                "photo": "https://domain.com/sender-link.jpg"
                            },
                            "to": {
                                "_id": "7b3b757f75f5df138702e968",
                                "username": "recipient_username",
                                "photo": "https://domain.com/recipient-link.jpg"
                            },
                            "status": "waiting",
                            "timestamp": "2026-06-12T11:51:28.000000"
                        }
                    ]
                },
                {
                    "requests": []
                }
            ]
        }
    }


class InsertRequestModel(BaseModel):
    to: RequestUserModel
    status: RequestStatusEnum = "waiting"
    timestamp: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "to": {
                        "_id": "7b3b757f75f5df138702e968",
                        "username": "recipient_username",
                        "photo": "https://domain.com/recipient-link.jpg"
                    },
                    "status": "waiting"
                }
            ]
        }
    }