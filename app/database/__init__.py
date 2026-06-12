from typing import Any
import os

from pymongo import AsyncMongoClient

client = AsyncMongoClient(os.getenv("MONGO_URI"))
mongodb = client[os.getenv("MONGO_DB")]

def filter_options(
    options: dict[str, Any], 
    allow_raise = True
) -> dict[str, Any]:
    filtered_options = {k: v for k, v in filter(
        lambda v: v[1] is not None, options.items())
    }

    if not filter_options and allow_raise:
        raise ValueError("options are empty, nothing to filter")
    
    return filtered_options