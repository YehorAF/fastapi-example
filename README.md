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
async def post_some_information():
    ...


@app.put("/api")
async def put_some_information():
    ...


@app.delete("/api")
async def delete_some_information():
    ...
```

## APIRouter

It is instance that handles routing. `APIRouter` used to split routers on diffrenet files. It has not functionality and method (`mount`, `exception_handler`, `middleware` etc.), but it has HTTP methods (`get`, `post`, `put` etc.) and `websocket`. You can use it following way:

- Imagine you have following project structure
    - `./app`
        - `main.py`
        - `__init__.py`
        - `/handlers`
            - `router.py`
            - `__init__.py`

- In `app/handlers/router.py` you can define specific router
```python
from fastapi import APIRouter

router = APIRouter(prefix="/router") # you can use prefix to define path


@router.get("/hello")
async def send_hello_from_router():
    return "hello"

```

- In `app/main.py` you can join to FastAPI the router
```python
from fastapi import FastAPI

from handlers.router import router

app = FastAPI()
app.include_router(router)
```

How it is designed in example:

- Structure:
```sh
app
├───main.py
├───__init__.py
├───cache
├───certificates
├───database
├───handlers
│   ├───days.py
│   ├───requests.py
│   ├───users.py
│   ├───views.py
│   ├───__init__.py
├───schemas
├───static
│   ├───css
│   └───js
├───templates
└───utils
```
- Code:
```python
# days.py
from fastapi import APIRouter

days_router = APIRouter(prefix="/api/days")
```

```python
# requests.py
from fastapi import APIRouter

requests_router = APIRouter(prefix="/api/requests")
```

```python
# users.py
from fastapi import APIRouter

users_router = APIRouter(prefix="/api/users")
```

```python
# views.py
from fastapi import APIRouter

views_router = APIRouter()
```

```python
# main.py
from fastapi import FastAPI

from handlers.views import views_router
from handlers.users import users_router
from handlers.requests import requests_router
from handlers.days import days_router

app = FastAPI()

app.include_router(views_router)
app.include_router(users_router)
app.include_router(requests_router)
app.include_router(days_router)
```

More information about it by [link](https://fastapi.tiangolo.com/tutorial/bigger-applications/). 

# URL params

FastAPI URL handling based on [Starlette](https://starlette.dev). Due to it you can reference on the documentation to check possibility of using. You can define your router path with `{}` and write keyword in them, which then you can parse:

```python
@app.get("/some_thing/{thing_id}")
async def get_some_thing(thing_id: int):
    return thing_id
```

You can filter them by value type:
```python
@app.get("/values/{value: int}")
async def get_int_value(value: int):
    return f"integer value: {value}"
    
    
@app.get("/values/{value: str}")
async def get_str_value(value: str):
    return f"string value: {value}"
```

Also if you use filtering by type, you should following:

```python

# you never get value from function get_my_value because {value: str} and my 
# have same types and get_str_value cathc it
@app.get("/values/{value}")
async def get_str_value(value: str):
    return f"string value: {value}"


@app.get("/values/my")
async def get_my_value():
    return "my value"


# instead you should use it next way
@app.get("/values/my")
async def get_my_value():
    return "my value"


@app.get("/values/{value}")
async def get_str_value(value: str):
    return f"string value: {value}"
```

You can filter only primitive types such as: int, float, str, uuid, path. If you want to handle own type, more information you can get [there](https://starlette.dev/routing/#path-parameters)


You have several ways to filter parameters in the router:
- describe in function parameters with defined type
- describe in function parameters with Query
- use pydantic.BaseModel

How you can just describe in function parameters:
```python
@app.get("/values")
async def get_filtered_values(
    skip: int, # required parameter. if it is missed, app sends error
    limit: int = 20, # set default value but you can use only integers
    q: str | None = None, # string or None
    do_not_use: list[str] = ["v1", "v2"] # list of strings
):
    pass
```

That `do_not_use` get all arguments correctly, you should define your URL params next way:  `&do_not_use=v1&do_not_use=v4&do_not_use=v2`. If you try to set different option such as `do_not_use=["v1", "v2", "v3"]` it parse as string.

If you want to check your parameters you should use Query() with Annotated. How it looks:
```python
from typing import Annotated

from fastapi import FastAPI, Query

@app.get("/values")
async def get_filtered_values(
    skip: Annotated[int, Query(ge=0)], # greater or equal to 0, but required
    limit: Annotated[int, Query(ge=1, le=20)] = 20, # greater or equal, lether or equal
    q: Annotated[str | None, Query(min_length=2, max_length=50)] = None, # maximal and minimal character length
    user: Annotated[str | None, Query(min_length=9, max_length=37, pattern="@\w+")] # with regular expression pattern
)
```

For filtering and validation you can use `pydantic.BaseModel`. In the example described this method, because it provides specific validation possibilities:
```python
# app/schemas/queries.py

from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from schemas import ReactionEnum, PyObjectId

# converts bson.ObjectId to string
# PyObjectId = Annotated[str, BeforeValidator(str)]


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

```

# Request/Response Schemas

## Requests. Body

## Requests. Form

## Requests. Pydantic BaseModel

## Responses. Response

## Responses. JSON Response

## Responses. Form

## Responses. HTMLResponse

## Responses. Pydantic BaseModel

# Headers and cookies

# File Handling

## UploadFile, File

## StaticFiles

## Templates

# CRUD and 

# Exception handle

# How to start

## Venv

## Docker