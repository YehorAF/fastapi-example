import bson
from typing import Annotated, Any
import os

from fastapi import APIRouter, Request, Depends, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schemas import PyObjectId
from schemas.queries import QueryDays, QueryRequests
from utils.dependencies import is_authed

from database.users import get_user as mongo_get_user
from database.days import (
    get_day_list_with_checking as mongo_get_day_list_with_checking
)
from database.requests import (
    get_request_list_with_checking as mongo_get_request_list_with_checking
)

views_router = APIRouter()
templates = Jinja2Templates("templates")


@views_router.get("/",response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@views_router.get("/auth", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse(
        request, 
        "auth.html", 
        {"password_hash_key": os.getenv("PRV_KEY"), "hash_type": "RS256"}
    )


@views_router.get("/show_user/{user_id}", response_class=HTMLResponse)
async def load_user(
    request: Request, 
    user_id: PyObjectId,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    my_id = bson.ObjectId(user_cache["user_id"])
    user_ids = []

    if bson.ObjectId.is_valid(user_id):
        user_id = bson.ObjectId(user_id)

    if user_id == "me" or user_id == my_id:
        res = await mongo_get_user(my_id)
        res |= {"is_me": True}
    elif isinstance(user_id, bson.ObjectId):
        res = await mongo_get_user(user_id, friend_id=my_id)

        if not res:
            raise HTTPException(404, "there is not such user")

        user_ids.append(user_id)
        res |= {"friends": []}
    else:
        raise HTTPException(404, "there are not such user")

    days = await mongo_get_day_list_with_checking(
        user_id=my_id, user_ids=user_ids, is_my=res.get("is_me"))

    return templates.TemplateResponse(request, "user.html", res | {"days": days})

    
@views_router.get("/show_days", response_class=HTMLResponse)
async def load_days(
    request: Request,
    query: Annotated[QueryDays, Query()],
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    skip = query.skip
    limit = query.limit
    user_id = bson.ObjectId(user_cache["user_id"])
    res = await mongo_get_day_list_with_checking(
        user_id=user_id, 
        limit=limit + 1, 
        **query.model_dump(by_alias=True, exclude=["limit"])
    )
    
    return templates.TemplateResponse(
        request=request, 
        name="days.html", 
        context={
            "days": res[:limit], 
            "is_prev": skip >= limit, 
            "is_next": (res_len := len(res) - 1) > 0 and res_len % limit == 0
        }
    )


@views_router.get("/insert_day", response_class=HTMLResponse)
async def load_insert_day_form(
    request: Request,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    return templates.TemplateResponse(request, "insert_day.html")


@views_router.get("/show_requests", response_class=HTMLResponse)
async def load_requests(
    request: Request,
    query: Annotated[QueryRequests, Query()],
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    my_id = bson.ObjectId(user_cache["user_id"])
    res_me = await mongo_get_request_list_with_checking(
        my_id=my_id, 
        query_type="me", 
        **query.model_dump(by_alias=True, exclude=["query_type"])
    )
    res_my = await mongo_get_request_list_with_checking(
        my_id=my_id, 
        query_type="my", 
        **query.model_dump(by_alias=True, exclude=["query_type"])
    )

    return templates.TemplateResponse(
        request, "requests.html", {"me": res_me, "my": res_my})