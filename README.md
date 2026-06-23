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
    return {"message": "hello"}

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
    return {"thing_id": thing_id}
```

You can filter them by value type:
```python
@app.get("/values/{value: int}")
async def get_int_value(value: int):
    return {"value": f"integer value: {value}"}
    
    
@app.get("/values/{value: str}")
async def get_str_value(value: str):
    return {"value": f"string value: {value}"}
```

Also if you use filtering by type, you should following:

```python

# you never get value from function get_my_value because {value: str} and my 
# have same types and get_str_value cathc it
@app.get("/values/{value}")
async def get_str_value(value: str):
    return {"value": f"string value: {value}"}


@app.get("/values/my")
async def get_my_value():
    return {"value": "my value"}
```

```python
# instead you should use it next way
@app.get("/values/my")
async def get_my_value():
    return {"value":: "my value"}


@app.get("/values/{value}")
async def get_str_value(value: str):
    return {"value": f"string value: {value}"}
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

# BaseModel provides value validation using 
# typing instances, built-in decorattors and validation classes
class TimeValidation(BaseModel):

    # there we use such method to init min_timestamp and max_timestamp attributes.
    # check_fields=False -- do not check attributes of class
    # firstly, it calls for min_timestamp, then it calls for max_timestamp
    @field_validator("min_timestamp", "max_timestamp", check_fields=False)
    @classmethod
    def validate_by_one(cls, value):
        return value
    

    # there we can validate max_timestamp and min_timestamp.
    # due to validate_by_one which was before we can call validation once
    # and check defined attributes.
    @field_validator("max_timestamp", check_fields=False)
    @classmethod
    def check_time(cls, value, info) -> datetime: # value ~ max_timestamp, 
                                                  # info.data ~ processed attributes

        # checks if min_timestamp and max_timestamp not None to compare them
        if (info.data["min_timestamp"] and 
            value and 
            info.data["min_timestamp"] > value):
            raise ValueError("Correct your time range")
        return value
    

    # Literal checks if value equial to specified values without type validation.
    # that is why we should use field_validator to cast it into integer
    # and then gives to Literal
    @field_validator("sort", check_fields=False, mode="before")
    @classmethod
    def check_sort(cls, value, info) -> int:
        try:
            value = int(value)
        except TypeError:
            raise TypeError("sort should be integer")
        
        return value

# inherit TimeValidation
class QueryDays(TimeValidation):
    reactions: list[ReactionEnum] = Field(
        ["awful", "bad", "normal", "good", "awesome"]
    ) # we can use pydantic.Field as Query
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    limit: int = Field(default=20, ge=1, le=20)
    skip: int = Field(default=0, ge=0)
    sort: Literal[-1, 1] = -1
    sort_by: str = "_id"
    is_my: bool = False
```

How we can use it for routins params validation:

```python
from fastapi import APIRouter, Query, Depends

...

from schemas.queries import QueryDays
from utils.dependencies import is_authed

...

days_router = APIRouter(prefix="/api/days")


@days_router.get("/", response_model=GetDayListModel)
async def get_day_list(
    query: Annotated[QueryDays, Query()], # because we define type/instance, 
                                          # we do not use "="
    user_cache: Annotated[dict[str, Any], Depends(is_authed)] # it will be later
):
    ...
```

# Request/Response Schemas

OpenAPI provides possibility of defining your API schema using different tools, in example, pydantic.BaseModel and built-in JSONResponse, HTMLResponse, Form etc. 

## Requests. Pydantic BaseModel

The basic and most correct variant is using pydantic.BaseModel for handaling data. But it **recieves only JSON-like data** requests. How to use it:

```python
from typing import Optional

# pydantic provides different types to validate basic data
from pydantic import BaseModel, EmailStr, FilePath, AnyUrl, Field

# but pydantic does not support bson.ObjectId that is why
# you should use own solution
from schemas import PyObjectId


class UserModel(BaseModel):
    # you can use prydantic.Filed to validate attributes.
    # "alias" provides declaring another attribute variation
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: EmailStr
    username: str = Field(min_length=8, max_length=32)
    photo: Optional[FilePath | AnyUrl] = None # Optional[some_type] ~ None or some_type 

    ...


class GetMeModel(UserModel):
    friends: list[UserModel] # we can use it in such case also

    ...

class InsertUserModel(UserModel):
    password: str

    ...
```

How to declare it in function:
```python

@users_router.post("/me/sign")
async def sign_user(
    request: Request, # it is needed for another action
    user: InsertUserModel
):
    ...
```

Request data example:
```json
{
    "email": "new_user@gmail.com",
    "username": "new_player_123",
    "photo": "https://domain.com/avatar.jpg",
    "password": "SuperSecurePassword123!"
}
```

If we want send multiple parameters, you can do next:
```python
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Header

class A(BaseModel):
    id: int
    value: str
    tags: list[str]

class B(BaseModel):
    id: int
    depricated_a: list[A]


app = FastAPI()


@app.post("/insert_some_value/{some_id}")
async def insert_some_value(
    some_id: int,
    a: A, 
    b: B, 
    user_agent: Annotated[str, Header()], # it parses automatically
    q: str | None = None, # URL parameter
    limit: int = 20 # URL parameter
):
    ...
```

In such case request data looks like:
```json
{
    "a": {
        "id": 1,
        "value": "long-value",
        "tags": ["t1", "t2"]
    },
    "b": {
        "id": 1,
        "depricated_a": [
            {
                "id": 2,
                "value": "ABC",
                "tags": ["t1", "t2"]
            },
            {
                "id": 3,
                "value": "123",
                "tags": ["t1", "t2"]
            }
        ]
    }
}
```

You should just split on different fields. Also you can use it with query, path and header parameters.

## Requests. Body

If you want to send buil-in data asuch as previous example but for one item or define additional body parameter you should use next:

```python
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Body

class A(BaseModel):
    id: int
    value: str
    tags: list[str]


app = FastAPI()



@app.post("/send_something")
async def send_something(a: Annotated[A, Body(embed=True)]):
    # request example
    # {
    #     "a": {
    #         "id": 1,
    #         "value": "long-value",
    #         "tags": ["t1", "t2"]
    #     }
    # }
    ...

@app.post("send_not_declared_body_params")
async def send_not_declared_body_params(
    a: Annotated[int, Body()],
    b: Annotated[str, Body()]
):
    # request example
    # {
    #     "a": 1,
    #     "b": "some string"
    # }
    ...
```

## Requests. Form

When your client sends request data in `multipart/form-data` format, you cannot process as JSON and due to with BaseModel, because it expects JSON format. FastAPI provides instance Form which can parse form-data:
```python
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Form

class A(BaseModel):
    id: int
    value: str


app = FastAPI()

@app.post("/post_a")
async def post_form(a: Annotated[A, Form()]):
    """
    expected request
    {
        "id": 1,
        "value": "string value",
    }
    """
    ...


@app.post("/post_one_value")
async def post_one_value(value: Annotated[str, Form()]):
    """
    expected request
    {
        "value": "string value"
    }
    """
    ...
```

You can not combine JSON and form-data, but you can get query, path, header and cookie parameters.

## Responses. JSONResponse and BaseModel

As default FastAPI sends response as plan text, but if you want to send json response, you should use JSONResponse or BaseModel, for the last you can describe data and use it for documentation.

```python
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import JSONResponse


class A(BaseModel):
    id: int
    value: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "value": "string value"
                }
            ]
        }
    }


app = FastAPI()

# we can init our response model that user can see it
@app.get("/get_a", response_model=A)
async def get_a():
    return {"id": 1, "value": "string value"}


# in this case user can not see response schema
@app.get("/get_json_data")
async def get_json_data():
    return JSONResponse({"value": "hello there!"})
```

## Responses. HTMLResponse

FastAPI gives you send HTML pages and create templates for them (more information in "File Handling => Templates")

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/pages/1")
async def get_page1():
    return HTMLResponse("<h1>Hello there</h1>")

    
@app.get("/pages/2", response_class=HTMLResponse)
async def get_page2():
    return "<h1>Wow! You on the second page</h1>"
```

## Responses. RedirectResponse

Sometimes you want to redirect user after correct or incorrect request on server side. You can use RedirectResponse:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/jsut_redirect_me")
async def just_redirect_me():
    # aiohttp uses "raise" with HTTPFound etc. classes
    # to redirect on another page. 
    # that approcach is better sometimes, when you want redirect from 
    # some function or block of codes 
    return RedirectResponse("/get_out_there")
```

For sending exceptions such as 404 or 403 we use HTTPException, what will be described below.

# Headers and cookies

For security, authorization and processing specific data you should handle header and cookie fields. FastAPI provides different approaches to work with them.

You can parse cookies and headers in function attributes:
```python
from typing import Annotated

from fastapi import FastAPI, Cookie, Header

app = FastAPI()

# FastApi provides auto converting
@app.get("/check_headers")
async def check_headers(
    user_agent: Annotated[str | None, Header()] = None, # User-Agent => user_agent
    x_user_id: Annotated[str | None, Header()] = None, # X-User-Id => x_user_id
    some_value: Annotated[str | None, Header(convert_underscores=False)] = None, # disable auto converting
    token: Annotated[str | None, Cookie()] = None, # parses field "Cookies" 
                                                   # and takes value from attribute
                                                   # token
    session: Annotated[str | None, Cookie()] = None # without None it will be required
):
    return {
        "user_agent": user_agent,
        "x_user_id": x_user_id,
        "some_value": some_value,
        "token": token,
        "session": session,
    }
```

Also it is possible to define headers in BaseModel and parse them in function:
```python
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, Cookie, Header


class HeaderModel(BaseModel):
    x_token: str | None = None # if 
    x_user_id: str | None = None


class CookieModel(BaseModel):
    token: str | None = None
    session: str | None = None


@app.get("/check_headers")
async def check_headers(
    headers: Annotated[HeaderModel, Header()],
    cookies: Annotated[CookieModel, Cookie()]
):
    return {
        "headers": headers.model_dump()
        "cookies": cookies.model_dump()
    }
```

But you can manually get paramteres from the Request:
```python
# example from app/utils/dependencies.py
from fastapi import Request, HTTPException

from cache.crud import get_user_from_cache
from utils.exceptions import TokenException


async def is_admin(request: Request):
    # request.cookies and request.headers have Map instance that provides
    # dict methods to get data and declines updation data methods
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)

    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)
    
    if values["status"] != "admin":
        raise HTTPException(
            status_code=403, detail=f"you are not admin")
    
    return values | {"token": token}
```

To add cookies or headers you should initialize any Response instance (JSONResponse, HTMLResponse, RedirectResponse etc.) and using method `set_cookie()` (for cookies) or get attribute `headers` and method `append()` (for header) add value
```python
# example from app/handlers/users.py
@users_router.post("/me/sign")
async def sign_user(request: Request, user: InsertUserModel):
    pk = crypto.PKey()
    pk.generate_key(crypto.TYPE_RSA, 512)
    salt = crypto.dump_privatekey(crypto.FILETYPE_PEM, pk)
    password = jwt.encode({"password": user.password}, salt, algorithm="RS256")

    try:
        res = await mongo_insert_user(
            **user.model_dump(exclude=["password"]), salt=salt, password=password)
        inserted_id = str(res.inserted_id)
    except DuplicateKeyError as err:
        raise HTTPException(
            400, 
            "Account with such email or username have already created"
        )
    except Exception as err:
        raise HTTPException(400, str(err)) # add information

    token = uuid.uuid4().hex
    exp_time = int(os.getenv("EXP_TIME")) or 2592000

    await cache_user(
        request.client.host, inserted_id, token, "user", exp_time
    )

    # you can add headers only when you init Response instance
    response = JSONResponse(content={}, headers={"X-UserId": inserted_id})

    # set token value (key, value, expire time)
    response.set_cookie(
        "token", 
        token, 
        exp_time,
    )

    return response
```

If you want to delete cookie, you should use method `delete_cookie()`:
```python
# example from app/handlers/users.py
@users_router.post("/me/quit")
async def quit_account(user_cache: Annotated[dict[str, Any], Depends(is_authed)]):
    await delete_user_cache(user_cache["token"])

    response = JSONResponse({"detail": "user token was removed"})
    response.delete_cookie("token") # it will remove defiend cookie value on client side

    return response
```  

# Dependencies

Dependencies provide middleware or decorator functionality, but the main difference from middleware is that it works only on defined functions or routers and before function starts. For our example we use dependencies to check if user signed in application and if he has special rights. In another cases you can use it for data validation, pass specific parameters etc.

How we init our dependency function:
```python
# app/utils/dependencies.py
from fastapi import Request, HTTPException

from cache.crud import get_user_from_cache
from utils.exceptions import TokenException

# we can not pass values in annotations block that is why we should
# use teo function that provides same functionality
async def is_admin(request: Request): # in dependency we can use all attributes, which are used in function
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)

    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)
    
    if values["status"] != "admin":
        raise HTTPException(
            status_code=403, detail=f"you are not admin")
    
    return values | {"token": token} # we can send specific value


async def is_authed(request: Request):
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)
    
    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)

    # better to use on startup to set statuses
    if values["status"] not in ["admin", "user", "client"]:
        raise HTTPException(
            status_code=403, 
            detail=f"you have not access there without any status")
    
    return values | {"token": token}
```

How we can use it in function:
```python
# app/handlers/users.py
@users_router.post("/me/quit")
async def quit_account(user_cache: Annotated[dict[str, Any], Depends(is_authed)]):
    await delete_user_cache(user_cache["token"])

    response = JSONResponse({"detail": "user token was removed"})
    response.delete_cookie("token")

    return response
```

Also it is allowed to use next methods:
```python
from typing import Annotated

from fastapi import FastAPI, Depends, Header 

# it works under methods __init__ (initialize class) and __call__ (class is used as function)
class CheckParams:
    def __init__(self, q: str | None, skip: int = 0, limit: int = 20):
        self.q = q
        self.skip = skip
        self.limit = limit

# we can use dependency in another dependency
async def check_params_and_get_token(
    params: Annotated[CheckParams, Depends()], # due to instance will ne called we can use this structure
    x_token: Annotated[str, Header()]
):
    return {"params": params, "x_token": x_token}

# it is pseudocode that is why it will not work
# we can initialize connection and pass it to function as arguemnt
# than after completion or erro close it
# alos it works with "with" or "async with"
def yield_db():
    db = SomeDBInstance()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/check_dependencies")
def check_dependencies(
    params: Annotated[dict, Depends(check_params_and_get_token)], # we can use async dependencies in sync function and otherway
    db: Annotated[SomeDBInstance, yield_db]
):
    ...
```

More information about using [dependency as class](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1), [global dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/) and [another examples](https://fastapi.tiangolo.com/tutorial/dependencies/) in FastAPI documentation. But it is better keep it simple and do not complecate dependencies (complex database requests, requests to external APIs, calculation etc.) because it will slow every client request processing and reduce server efficiency.

# File Handling

FastAPI provides different variations to handle file for different tasks. For HTML file hadnling we can use Jinja2, for staric files such as JS scripts, CSS and some images we can use StaticFiles and for dynamic files we can use third-party tools such as Azure Blob Storage and Nextcloud or provide own solution.

## UploadFile, File

We can use it to handle user loaded files such as photos or documents. For them we data-multipart requests. There are two instances which handle user files: File and UploadFile. File we can use for small files because it loads them all and saves in RAM until has processed them:

```python
from typing import Annotated

from fastapi import FastAPI, File

app = FastAPI()


@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()] # file is loaded as bytes once
):
    ...
```

How we can handle larger files:

```python
# app/handlers/users.py
@users_router.post("/me/photo/upload")
async def upload_photo(
    file: UploadFile, # declare file instance, firslty it sends schema and then data
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    user_id = bson.ObjectId(user_cache["user_id"])
    dir_uri = f"{os.getenv('PUBLIC_DIR')}/users/{user_id}" # use pathlib instead of this
    photo_uri = f"{dir_uri}/{user_id}-{file.filename}"

    # creates or clears user directory with photos
    create_or_clear_dir(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

    # creates and opens file
    async with aiofiles.open(f"{os.getenv('PRJ_DIR')}/{photo_uri}", "wb") as fp:
        while True:
            # reads file data until does not get EOF
            if (data := await file.read(int(os.getenv("FILE_SIZE")) or 1024)):
                # in such case data is delivered by chunks from client to server
                # when chunk is loaded and written interpretator free it and load next
                # that is why large files can not lead to memory issue
               await fp.write(data)
            else:
                break

    # set link on new user photo
    res = await mongo_update_user(user_id, photo=photo_uri)

    if res.modified_count < 1:
        shutil.rmtree(f"{os.getenv('PRJ_DIR')}/{dir_uri}")

        raise HTTPException(400, "user was not updated with photo")
    
    return JSONResponse({"detail": "photo was uploaded"})
```

Also we can upload several files:

```python
import aiofiles

from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/load_several_files")
async def load_several_files(files: list[UploadFile]):
    # go through list and load all files
    for i, file in zip(range(len(files)), files):
        async with aiofiles.open(f"file{i}-{file.filename}", "wb") as fp:
            while True:
                if (data := await file.read):
                    await fp.write(data)
                else:
                    break
```

If we want to give user defined file, we can use StreamingResponse and AsyncIterable/Iterable:

```python
# app/main.py
@app.get("/public/{dir}/{dir_id}/{filename}", response_class=StreamingResponse)
async def handle_files(
    dir: str,
    dir_id: str,
    filename: str,
    request: Request, 
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
) -> AsyncIterable[bytes]:
    path = (
        f"{os.getenv('PRJ_DIR')}{os.getenv('PUBLIC_DIR')}/"
        f"{dir}/{dir_id}/{filename}"
    )
    try:
        # open and read file by bytes 
        async with aiofiles.open(path, "rb") as fp:
            while True: 
                # read files by chunks
                if chunk := await fp.read(int(os.getenv("FILE_SIZE"))):
                    # send chunk of file to user
                    yield chunk
                else:
                    break
    except Exception as ex:
        raise HTTPException(404, "not such file")
```

StreamingResponse provides posibility to send video and adio files. On client side you can also play them while they are loading.

## StaticFiles

If you have static files that after deploying be unchangable, to broadcast them you can use StaticFiles. How it works:
1. Cretae folder with your static files
2. Initilize instance `StaticFiles` and set folder location and URL path
3. Use method `mount` to mount instance to app

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), "static")
```

Mount works in another way then routers. It mounts ASGI app (but it is also possible to use WSGI with specific settings) to defined path, that will be handeled this app. It means, that request to `/static/` will be handeled by StaticFiles, than it will process URL path and init for each content defined router. Due to it you can not load files and then try to get them without restarting application.

## Templates

If you have small application with several pages that do not need any JS content handling or you do not want to learn any JS framework for small project, you can use templates. FastAPI provides templating with Jinja2.

How you can use it in FastAPI:

```python
# app/handlers/views.py
views_router = APIRouter()
templates = Jinja2Templates("templates") # init Jinja2 templating, pass path to folder with templates

...
# because Jinj2 converts it into HTML you should use HTMLResponse
@views_router.get("/show_days", response_class=HTMLResponse)
async def load_days(
    request: Request, # it is necessary
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
    
    # process template
    return templates.TemplateResponse(
        request=request, 
        name="days.html", # path or name of html file
        context={ # you can pass arguemnts to html document
            "days": res[:limit], 
            "is_prev": skip >= limit, 
            "is_next": (res_len := len(res) - 1) > 0 and res_len % limit == 0
        }
    )
```

How it looks on document side:

```jinja
{# app/templates/base.html #}
<!DOCTYPE html>
<html>

<head>
    <title>{% block title %}{% endblock %}</title>
    {# cut scripts #}
    {% block scripts %}{% endblock %}
    {% block css %}{% endblock %}
</head>

<body>
    <nav id="app-nav" class="nav">
        ...
    </nav>
    <div id="log-message">
        ...
    </div>
    <main id="app-main">
        {% block app %}{% endblock %}
    </main>
    <footer id="app-footer"></footer>
</body>

</html>
```

```jinja
{# app/templates/days.html #}
{% extends "base.html" %} {# init template #}

{% block title %}Days{% endblock %}

{% block scripts %} 
<script type="module" src="/static/js/days.js"></script>
{% endblock %}

{% block css %} 
<link rel="stylesheet" href="/static/css/days.css">
{% endblock %}


{% block app %}

<div class="container my-5" style="max-width: 800px;">
    ...
    <div class="d-grid gap-4">
        {% for day in days%}

        <div id="day-{{ day._id }}" class="day-container card shadow-sm overflow-hidden border-light bg-white">
            <div class="info-container card-header bg-white d-flex align-items-center justify-content-between py-3 border-0">
                <div class="user-container d-flex align-items-center">
                    <figure class="mb-0 me-2">
                        {% if day.user.photo %}
                        <img src="{{ day.user.photo }}" class="rounded-circle object-fit-cover border" style="width: 38px; height: 38px;">
                        {% else %}
                        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png" class="rounded-circle border" style="width: 38px; height: 38px;">
                        {% endif %}
                    </figure>
                    <a href="views/users/{{ day.user._id }}" class="text-decoration-none">
                        <header class="fw-bold text-dark mb-0">{{ day.user.username }}</header>
                    </a>
                </div>
                <div class="d-flex flex-column align-items-end small text-muted" style="font-size: 0.75rem;">
                    <span class="timestamp">Created: {{ day.created }}</span>
                    {% if day.last_updated %}
                    <span class="timestamp">Last updated: {{ day.last_updated }}</span>
                    {% endif %}
                </div>
            </div>
            
            <figure class="mb-0 border-vertical text-center bg-light">
                {% if day.photo %}
                <img src="/{{ day.photo }}" class="img-fluid w-100 object-fit-cover" style="max-height: 450px;">
                {% endif %}
            </figure>
            
            <div class="card-body p-4">
                <span class="d-block mb-2 fw-medium text-dark">
                    How was it going? 
                    <a class="reaction badge bg-info text-dark text-decoration-none ms-1 text-capitalize">{{ day.reaction }}</a>
                </span>
                <p class="card-text text-secondary mb-0" style="white-space: pre-wrap;">{{ day.description }}</p>
            </div>
        </div>

        {% endfor %}
    </div>

    <nav class="nav-page-btns d-flex justify-content-center gap-3 mt-5 border-top pt-4">
        <a id="previous-days" class="btn btn-outline-secondary px-4 btn-sm fw-semibold text-decoration-none {% if not is_prev %}disabled{% endif %}" style="cursor: pointer;" {% if not is_prev %}aria-disabled="true"{% endif %}>previous</a>
        <a id="next-days" class="btn btn-outline-primary px-4 btn-sm fw-semibold text-decoration-none {% if not is_next %}disabled{% endif %}" style="cursor: pointer;" {% if not is_next %}aria-disabled="true"{% endif %}>next</a>
    </nav>

</div>

{% endblock %}
```

For templates we can init base file `base.html` where we have described basic libs, navigation, footer etc. If we need to initialize changable element which is depending on defined file we can use `{% block <block_name> %}{% endblock %}`. To get base template we should use `{% extends "<base_file_name>" %}`. 

If we want use data that was sent from FastAPI router we can get it with `{{ <var_name> }}`. If variable is dict/json, we can get access to data with point and attribute name: `{{ dict.attribute }}`. If we have list we can get with defined location number `{{ list[0] }}` or with `{% for var in list %}{% endfor %}`. 

Jinja2 provides if-statements: `{% if <python-statement> %}{% endif %}`. You can use python basic built-in python operations to check value. More information about Jinja2 templating you can find [there](https://jinja.palletsprojects.com/en/stable/templates/). 

Today is better to use JS/TS frameworks because they provide easier managing and rendering data on client side, in example, loading new content, changing data, animations etc. With Jinja2 not provides basic templates as Dash or DjangoForms, for animations, form manipulations etc. you will use JS any way without useStates (or similar methods), effective localStorage or caching, comfortable project structure with defined components.

# Exception handling

FastAPI provides instrument to handle excpetions. It works as middleware which catches all exceptions from router functions and processes them. You can create own exception and catch it in the function:
```python
# app/utils/exceptions.py
class TokenException(Exception):
    def __init__(self, name):
        self.is_api = "api" in name
        self.name = f"you have not token to pass the page: {name}"
``` 

```python
# app/main.py
@app.exception_handler(TokenException) # you should use this decorator to cathc exceptions
async def handle_token_issue(request: Request, exc: TokenException):
    # you can raise another exception or return specific response
    if exc.is_api:
        raise HTTPException(403, "you should auth to use api")

    response = RedirectResponse("/auth")
    response.delete_cookie("token")
    
    return response
```

You can use defined excpetions and catch several variations. It will help you split logic for routing and error handling that increase code clearness.

# CRUD

CRUD (create, read, update, delete) is basic data handling operations in the system. To split logic between data managing and routing in our example we have separated routers and database operations.

To use MongoDB we should initilize client instance which is responsible for MongoDB connection and database instance which is responsible for database managment operations:
```python
# app/database/__init__.py
from typing import Any
import os

# if we want to use async mode we should call AsyncMongoClient
# instead of MongoClient
from pymongo import AsyncMongoClient

client = AsyncMongoClient(os.getenv("MONGO_URI"))
mongodb = client[os.getenv("MONGO_DB")]
```

To send database requests we can use `mongodb` variable. It works next way: `mongodb.<collection_name>.<operation_method>`. To make code clearlier we should split CRUD functions between files by collections. Now we can write functions:
```python
# app/database/users.py
import bson
from typing import Literal, Any
from pymongo import UpdateOne

# import from __init__.py necessary objects and functions
# filter_options remove None values and returns ~clear~ dictionary
from database import mongodb, filter_options

# we should define function with verb what we will do with object and noun
async def get_user(
    # define every arguments for filtering
    user_id: bson.ObjectId = None,
    email: str = None,
    username: str = None,
    friend_id: bson.ObjectId = None,
    friend_email: str = None,
    fields = {"password": 0, "salt": 0},
    *args, **kwargs # if we get any additional field, which we do not use
):
    # find_one recives filetr options and fields which we need to get
    return await mongodb.users.find_one(
        filter_options({
            "_id": user_id,
            "username": username,
            "email": email,
            "friends._id": friend_id,
            "friends.email": friend_email,
        }), 
        fields
    )


async def get_user_list(
    ids: list[bson.ObjectId] = None,
    usernames: list[bson.ObjectId] = None,
    emails: list[bson.ObjectId] = None,
    sort: Literal[-1, 1] = 1,
    sort_by: str = "_id",
    skip: int = 0,
    limit: int = None,
    is_or: bool = False,
    fields={},
    *args, **kwargs
):
    # build specific filter options
    filtered_options = filter_options({
        "_id": {"$in": ids} if ids else None,
        "username": {"$in": usernames} if usernames else None,
        "email": {"$in": emails} if emails else None,
    })

    if is_or:
        filtered_options = {
            "$or": [{k: v} for k, v in filtered_options.items()]
        }

    # beacause find returns async cursor and point at defined document
    # we can use process methods such as sort, skip, limit etc.
    # also these methods returns another cursor on filtered documents.
    # you can parse them with "async for" which gives you element by one
    # and can save RAM or load them all and convert to list with method to_list.
    # in this case you may not use limit
    return await mongodb.users.find(
        filtered_options,
        {"password": 0, "salt": 0} | fields
    ).sort(sort_by, sort).skip(skip).to_list(limit)


async def insert_user(
    email: str,
    username: str,
    photo: str,
    salt: str,
    password: str,
    status: Literal["user", "admin"] = "user",
    *args, **kwargs
):
    # it returns InsertResultOne with insertion status and document ObjectId.
    # you should convert values into dictionary.
    # "insert_many" returns InsertResultMany with similar result but instead of
    # ObjectId or None it gives ObjectId list 
    return await mongodb.users.insert_one({
        "email": email,
        "username": username,
        "photo": photo,
        "salt": salt,
        "password": password,
        "status": status,
        "friends": []
    })


async def update_user(
    user_id: bson.ObjectId,
    email: str = None,
    password: str = None,
    photo: str = None,
    status: Literal["user", "admin"] = None,
    *args, **kwargs
):
    # for update operation you should firstly set filter dictionary
    # and then define update method with new fields.
    # it returns UpdateResult with status (how much was modified etc.) 
    # and upserted_ids if you set True for upsertion operation
    # (inserts document if not found existed).
    return await mongodb.users.update_one(
        {"_id": user_id},
        {"$set": filter_options({
            "email": email,
            "password": password,
            "photo": photo,
            "status": status
        })}
    )


async def add_friends_to_users(user1: dict[str, Any], user2: dict[str, Any]):
    # we can use method bulk_write for several insertion, updating, deletion
    # operations in one request. it returns BulkWriteResult
    return await mongodb.users.bulk_write([
        UpdateOne({"_id": user1["_id"]}, {"$push": {"friends": user2}}),
        UpdateOne({"_id": user2["_id"]}, {"$push": {"friends": user1}}),
    ])


async def remove_friends_from_user(
    user1_id: bson.ObjectId, 
    user2_id: bson.ObjectId
):
    return await mongodb.users.bulk_write([
        UpdateOne({"_id": user1_id}, {"$pull": {"friends": {"_id": user2_id}}}),
        UpdateOne({"_id": user2_id}, {"$pull": {"friends": {"_id": user1_id}}})
    ])


async def delete_user(user_id: bson.ObjectId):
    # to delete_one and delete_many delete documents and returns DeleteResult.
    # it recieves only filter options
    return await mongodb.users.delete_one({"_id": user_id})
```

More infromation about bulk_write you can find [there](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/bulk-write/)

If we want to find document and [update](https://www.geeksforgeeks.org/python/python-mongodb-find_one_and_update-query/), [replace](https://www.geeksforgeeks.org/python/python-mongodb-find_one_and_replace-query/) or [delete](https://www.geeksforgeeks.org/python/python-mongoddb-find_one_and_delete-query/), we should use `find_one_<operation_name>` method. How we use one in example:

```python
# app/database/requests.py
async def find_and_delete_request(
    request_id: bson.ObjectId,
    reciever_id: bson.ObjectId,
    *args, **kwargs
):
    # it returns dictionary or None and do operation. For update 
    return await mongodb.requests.find_one_and_delete(
        {"_id": request_id, "to._id": reciever_id}
    )
```

Now you can use defined functions in handlers:

```python
# app/handlers/days.py
@days_router.post("/")
async def add_day(
    day: DayModel,
    user_cache: Annotated[dict[str, Any], Depends(is_authed)]
):
    # database.users.get_user
    user = await mongo_get_user(bson.ObjectId(user_cache["user_id"]))

    # database.days.insert_day
    res = await mongo_insert_day(
        user_id=user["_id"],
        username=user["username"],
        email=user["email"],
        user_photo=user["photo"],
        **day.model_dump(by_alias=True, exclude_none=True) # used alias and returns values without None
    )

    day_id = res.inserted_id
    if not day_id:
        raise HTTPException(400, "cannot insert day")

    return JSONResponse({"detail": "day was inserted", "day_id": str(day_id)})
```

Also it is possible to use SQLAlchemy ([sync](https://fastapi.tiangolo.com/tutorial/sql-databases/) and [async](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308)) and another SQL drivers or databases. Belowe are information about using Redis, where you can see, how you can handle it with FastAPI. 

# Caching

FastAPI does not have bult-in caching or cookie/session managment tools that is why you can find third-party library or provide caching yourself. The most popular and effectibvly solution for caching is Redis. We can use it a similar way as MongoDB.

```python
# app/cache/crur.py
from redis.asyncio import Redis

import os

# it is better to use ConnetionPool 
r = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=os.getenv("REDIS_DB"),
    decode_responses=True # if we want to get converted into object
)


async def cache_user(
    ip: str, 
    user_id: str, 
    token: str, 
    status: str,
    token_live = 2592000 # 30 days 60 * 60 * 24 * 30
):
    # we can set json-like objects in redis.
    # it automatically parse it for defined value to save
    await r.json().set(token, ".", {
        "ip": ip,
        "user_id": user_id,
        "status": status,
    })
    await r.expire(token, token_live) # set expire time on token


async def get_user_from_cache(token: str):
    return await r.json().get(token)


async def delete_user_cache(token: str):
    await r.json().delete(token)
```

And now we can use it in dependencies to check user authorization:

```python
async def is_authed(request: Request):
    if not (token := request.cookies.get("token")):
        raise TokenException(request.url.path)
    
    # there we try to get user values from cache
    if not (values := await get_user_from_cache(token)):
        raise TokenException(request.url.path)

    if values["status"] not in ["admin", "user", "client"]:
        raise HTTPException(
            status_code=403, 
            detail=f"you have not access there without any status")
    
    return values | {"token": token}
```

# Background tasks

FastAPI provides possibility to use background tasks for long-time operations such as email notifications (user loged in application from another device) or third-party API sending (you should check if user have signed in defined application). In these case you can just set some action and send response user with status "action is processing" and with websocket send response if it was successfull. How it looks:

```python
import asyncio
from pydantic import BaseModel

from fastapi import FastAPI, BackgroundTasks, 

lock = asyncio.Lock()
users_processed = []


class User(BaseModel):
    user_id: str
    message: str


async def pseudo_request_to_another_api(user: User):
    await asyncio.sleep(5)
    # do not use such method!!!

    async with lock:
        users_processed.append(user.model_dump())


app = FastAPI()


@app.websocket("/get_processed_users")
async def broadcast_processed_users(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(10)
        async with lock:
            await websocket.send_text(str(users_processed))


@app.post("/send_to_another_api_smth")
asycn def send_to_another_api_smth(
    background_tasks: BackgroundTasks
    user: User
):
    background_tasks.add_task(pseudo_request_to_another_api, user)
    return {"status": "success"}
```

If you have small app for small user amount this approach is the best but if you have more complicated functionality (image processing, file sending, data predicting etc.) it is better to use Celery. Also you can use SocketIO instead of provided library from FastAPI because it has more comfortable communication processing between client and server based on events and it has splitted user and room communication (send every user, which is connected to websocket, send only defined gorup, send only user)

# Celery

Celery is framework for distributed data processing. It provides Pub/Sub pattern for processing heavy tasks and task scheduling. In our example we use it to delete orphaned records (days and friends) and data updation in different collections. Celery does not support async processing that is why you should not use asynchronous clauses or you can work with them using `async_to_sync` from `asgiref` package. 

For our example i have rewritten CRUD operations due to specific tasks:

```python
# workres/crud.py
from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne, UpdateMany
import os

client = None
db = None

# we should use this construction due to connection issue possibility beacaouse
# celery works in different processes/containers/machines
def init_db():
    global client, db

    if not client:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("MONGO_DB")]

... # another crud functions

# an example of using lookup and data updating
def update_user_references():
    init_db()
    friend_batches = []
    request_batches = []
    day_batches = []

    max_del = int(os.getenv("MAX_DEL", 20))
    i = 0
    for res in db.users.find({}, {"email": 1, "username": 1, "photo": 1}):
        friend_batches.append(UpdateMany(
            {"friends._id": res["_id"]},
            {"$set": {
                "friends.$.email": res["email"],
                "friends.$.username": res["username"],
                "friends.$.photo": res["photo"],
            }}
        ))
        request_batches.append(UpdateMany(
            {"from_user._id": res["_id"]},
            {"$set": {
                "from_user.email": res["email"],
                "from_user.username": res["username"],
                "from_user.photo": res["photo"],
            }}
        ))
        day_batches.append(UpdateMany(
            {"user._id": res["_id"]},
            {"$set": { 
                "user.email": res["email"],
                "user.username": res["username"],
                "user.photo": res["photo"],
            }}
        ))

        if i and i % (max_del - 1) == 0:
            db.users.bulk_write(friend_batches)
            db.requests.bulk_write(request_batches)
            db.days.bulk_write(day_batches)

            friend_batches = []            
            request_batches = []
            day_batches = []

        i += 1

    if friend_batches:
        db.users.bulk_write(friend_batches)
        db.requests.bulk_write(request_batches)
        db.days.bulk_write(day_batches)

... # another crud functions
```

Now we can schedule our tasks:

```python
import dotenv
import logging
import os

if not os.getenv("REDIS_URI"):
    dotenv.load_dotenv()

from celery import Celery
from celery.signals import worker_process_init

import crud

# set up broker (we can use Redis)
app = Celery(
    "worker",
    broker=os.getenv("REDIS_URI"),
    backend=os.getenv("REDIS_URI")
)

# when worker starts
@worker_process_init.connect
def configure_workers(*args, **kwargs):
    crud.init_db()

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    ... # adding another periodic tasks
    sender.add_periodic_task(
        int(os.getenv("EXP_TIME", 60*60*12)), # define time where we should update
        update_user_references.s(),
        name="update user references"
    )

... # another task initializations

@app.task
def update_user_references():
    logging.info("update_user_references started")
    crud.update_user_references()
    logging.info("update_user_references finished")
```

We can start it with followind commands:
- `celery -A worker.app worker --loglevel=info` - starts workers (you should start it first)
- `celery -A worker.app beat --loglevel=info` - starts scheduler

If we have used celery in main app, it would look like:

```python
# celery file worker.py
import logging
import time

from celery import Celery

app = Celery(
    "worker",
    broker=os.getenv("REDIS_URI"),
    backend=os.getenv("REDIS_URI")
)

@app.task
def work_with_hard_task(task_id):
    logging.info(f"Hard task started: {task_id}")
    time.sleep(10)
    logging.info(f"Hard task ended: {task_id}")
```

```python
# fastapi file main.py
from fastapi import FastAPI

import worker

app = FastAPI()

@app.post("/start_hard_task/{task_id}")
async def start_hard_task(task_id: str):
    worker.work_with_hard_task(task_id)
    return {"status": "Hard task started"}
```

In this case you should:
- `celery -A worker app --loglevel=info` - start worker (you should start it first)
- `uvicorn main:app --host 127.0.0.1 --port 8080` - start fastapi

Without starting celery your tasks will not start working and ocures exception

# How to start

After lot of examples we can try start our application. There ware several ways to start/deploy it: manully or with docker. We try two ways. 

## Manually

First of all you should install [Python](https://www.python.org/downloads/), [MongoDB](https://www.mongodb.com/docs/manual/installation/) and [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/). Then you can change values of envirement variables such as EXP_TIME, FILE_SIZE etc. (if you already have installed MongoDB and Redis you should check their connection URLs) in `example.env` files and rename them to `.env`.

To configure virtual envirement and install libraries you should:
1) Open terminal and navigate to project directory: `cd <project_dir>`
2) Write following script `python3 -m venv .` and wait until it have not done
3) Then write `source bin/activate` (Linux/Mac) or `.\Scripts\activate` (Windows) to connect to loacl envirement
4) Enter and start `pip3 install -r requirements.txt`

Now you should split terminal on three windows and activate in every virtual enviroment:
- in first window locate to `app` folder and write `hypercorn main:app --bind 127.0.0.1:8080 --certfile=certificates/cert.pem --keyfile=certificates/key.pem` (it starts FastAPI app)
- in the second window enter `celery -A worker.app worker --loglevel=info` (it starts Celery worker)
- in the third run `celery -A worker.app beat --loglevel=info` (it starts Celery scheduler)

If you want stop them just close terminals or type in every `Ctrl+C` inreverse.

## Docker

# What were not included in the example