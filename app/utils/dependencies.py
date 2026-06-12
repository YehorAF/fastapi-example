from fastapi import Depends, Request, HTTPException

from cache.crud import get_user_from_cache
from utils.exceptions import TokenException


async def is_admin(request: Request):
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)

    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)
    
    if values["status"] != "admin":
        raise HTTPException(
            status_code=403, detail=f"you are not admin")
    
    return values | {"token": token}


async def is_authed(request: Request):
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)
    
    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)

    if values["status"] not in ["admin", "user", "client"]:
        raise HTTPException(
            status_code=403, 
            detail=f"you have not access there without any status")
    
    return values | {"token": token}