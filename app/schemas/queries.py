from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from schemas import ReactionEnum, PyObjectId


class TimeValidation(BaseModel):
    @field_validator("min_timestamp", "max_timestamp", check_fields=False)
    @classmethod
    def validate_by_one(cls, value):
        return value
    

    @field_validator("max_timestamp", check_fields=False)
    @classmethod
    def check_time(cls, value, info) -> datetime:
        if (info.data["min_timestamp"] and 
            value and 
            info.data["min_timestamp"] > value):
            raise ValueError("Correct your time range")
        return value
    

    @field_validator("sort", check_fields=False, mode="before")
    @classmethod
    def check_sort(cls, value, info) -> int:
        try:
            value = int(value)
        except TypeError:
            raise TypeError("sort should be integer")
        
        return value


class QueryDays(TimeValidation):
    reactions: list[ReactionEnum] = Field(
        ["awful", "bad", "normal", "good", "awesome"]
    )
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    limit: int = Field(default=20, ge=1, le=20)
    skip: int = Field(default=0, ge=0)
    sort: Literal[-1, 1] = -1
    sort_by: str = "_id"
    is_my: bool = False
    

class QueryRequests(TimeValidation):
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    query_type: Literal["me", "my"] = "me"
    sort: Literal[-1, 1] = -1
    sort_by: str = "_id"


class QueryFriends(BaseModel):
    ids: list[PyObjectId] | None = None