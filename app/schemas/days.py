from datetime import datetime
from typing import Optional
from pydantic import BaseModel, AnyUrl, FilePath, Field

from schemas import PyObjectId, ReactionEnum
from schemas.users import UserModel


class DayModel(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    reaction: ReactionEnum = "normal"
    description: str = Field(min_length=16, max_length=1024)
    photo: Optional[AnyUrl | FilePath] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "6a2a646f64f4cf027691d857",
                    "reaction": "normal",
                    "description": "hello hello hello hello",
                    "photo": "https://domain.com/long-link.jpg"
                },
                {
                    "reaction": "normal",
                    "description": "hello hello hello hello",
                }
            ]
        }
    }


class GetDayModel(DayModel):
    created: datetime
    last_updated: Optional[datetime] = None
    user: UserModel

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "6a2a646f64f4cf027691d857",
                    "reaction": "normal",
                    "description": "hello hello hello hello",
                    "photo": "https://domain.com/long-link.jpg",
                    "created": "2026-06-11T09:40:32.565000",
                    "user": {
                        "_id": "6a2a646f64f4cf027691d857",
                        "email": "email@gmail.com",
                        "username": "username",
                        "photo": "https://domain.com/long-link.jpg"
                    }
                },
                {
                    "id": "6a2a646f64f4cf027691d857",
                    "reaction": "normal",
                    "description": "hello hello hello hello",
                    "created": "2026-06-11T09:40:32.565000",
                    "last_updated": "2026-06-11T09:40:32.565000",
                    "user": {
                        "_id": "6a2a646f64f4cf027691d857",
                        "email": "email@gmail.com",
                        "username": "username",
                        "photo": "https://domain.com/long-link.jpg"
                    }
                }
            ]
        }
    }


class GetDayListModel(BaseModel):
    days: list[GetDayModel]

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "days": [
                        {
                            "id": "6a2a646f64f4cf027691d857",
                            "reaction": "normal",
                            "description": "hello hello hello hello",
                            "photo": "https://domain.com/long-link.jpg",
                            "created": "2026-06-11 09:40:32.565000",
                            "user": {
                                "_id": "6a2a646f64f4cf027691d857",
                                "email": "email@gmail.com",
                                "username": "username",
                                "photo": "https://domain.com/long-link.jpg"
                            }
                        },
                        {
                            "id": "6a2a646f64f4cf027691d857",
                            "reaction": "normal",
                            "description": "hello hello hello hello",
                            "created": "2026-06-11 09:40:32.565000",
                            "last_updated": "2026-06-11 09:40:32.565000",
                            "user": {
                                "_id": "6a2a646f64f4cf027691d857",
                                "email": "email@gmail.com",
                                "username": "username",
                                "photo": "https://domain.com/long-link.jpg"
                            }
                        }
                    ]
                },
                {
                    "days": []
                }
            ]
        }
    }