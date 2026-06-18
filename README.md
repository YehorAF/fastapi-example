# FastAPI Example

It is example of using FastAPI with MongoDB and Redis, that helps you create available enough application for real-world. It gives you understanding, how to build simple REST API, work with MongoDB, cache information to Redis, handle files, use Jinja2 and combine JS front-end with Pyton back end.

What does example present? It is web app which provides clients possibility to describe own day to them friends. It consists of authorization/registration page, main/index page, day list page, insert day page and user page. API has several main routers:
- / + all pages
- /api/users - user data handling
- /api/days - day data handling
- /api/requests - request data handling (provides functionality of friend adding)
- /statics - static files such as HTML, CSS, JS files and photos
- /public - user loaded files 

# Shorly about stack

## FastAPI

## MongoDB

## Redis

# Routing

## FastAPI

FastAPI is main instance, which provides all functionality of framework. Alos it provides data routing with following methods:
- `get` - method GET. Sends data in URL and headers. Is used to fetch data from server.
- `post` - method POST. Sends data in URL, headers and body. Is used to create or make something on server.
- `put` - method PUT. Sends data in URL, headers and body. Is used to update something.
- `delete` - method DELETE. Sends in URL and headers. Is used to delete something.
- `patch` - method PATCH, not used in example.
- `options` - method OPTIONS, not used in example.
- `connect` - method CONNECT, not used in example.
- `trace` - method TRACE, not used in example.

More information about HTTP methods [there](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods). How you can use it:

```python
from fastapi import FastAPI

app = FastAPI


@app.get("/api") # it is decorator. it is used as function wrapper 
                 # (preprocessing and postprocessing data function)
async def get_some_information(): # keyword "async" is used to define function as asynchronyous
    """It is a long string
    If you want describe function for user could see it in code editor
    or in /docs, you should use it function blick after it initialization.

    Also it save all user forming and parse **markdown signs**
    """
    ...


@app.post("/api")
async def post_some_infromation():
    ...


@app.put("/api")
async def put_some_information():
    ...


@app.delete("/api")
async def delete_some_information():
    ...
```

## APIRouter

It is instance that handles routing. `APIRouter` used for 

# URL params

# Request/Response Schemas

## Requests. Body

## Requests. Form

## Requests. Pydantic BaseModel

## Responses. Response

## Responses. JSON Response

## Responses. Form

## Responses. HTMLResponse

## Responses. Pydantic BaseModel

# File Handling

## UploadFile, File

## StaticFiles

## Templates

# CRUD and 

# Exception handle

# How to start

## Venv

## Docker