import aiofiles
import dotenv
from typing import Annotated, Any, Iterable
import os

if not os.getenv("MONGO_URI"):
    dotenv.load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse

from handlers.views import views_router
from handlers.users import users_router
from handlers.requests import requests_router
from handlers.days import days_router
from utils.dependencies import is_authed
from utils.exceptions import TokenException

app = FastAPI()


@app.exception_handler(TokenException)
async def handle_token_issue(request: Request, exc: TokenException):
    if exc.is_api:
        raise HTTPException(403, "you should auth to use api")

    return RedirectResponse("/auth")


@app.get("/public/{dir}/{dir_id}/{filename}", response_class=StreamingResponse)
async def handle_files(
    dir: str,
    dir_id: str,
    filename: str,
    request: Request, 
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    path = (
        f"{os.getenv('PRJ_DIR')}{os.getenv('PUBLIC_DIR')}/"
        f"{dir}/{dir_id}/{filename}"
    )
    try:
        async with aiofiles.open(path, "rb") as fp:
            while True: 
                if chunk := await fp.read(int(os.getenv("FILE_SIZE"))):
                    yield chunk
                else:
                    break
    except Exception as ex:
        print(ex)
        raise HTTPException(404, "not such file")



app.mount("/static", StaticFiles(directory="static"), "static")

app.include_router(views_router)
app.include_router(users_router)
app.include_router(requests_router)
app.include_router(days_router)

# hypercorn main:app --bind 127.0.0.1:8080 --certfile=certificates/cert.pem --keyfile=certificates/key.pem