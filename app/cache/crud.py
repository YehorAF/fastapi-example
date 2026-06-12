from redis.asyncio import Redis

import os

r = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=os.getenv("REDIS_DB"),
    decode_responses=True
)


async def cache_user(
    ip: str, 
    user_id: str, 
    token: str, 
    status: str,
    token_live = 2592000 # 30 days 60 * 60 * 24 * 30
):
    await r.json().set(token, ".", {
        "ip": ip,
        "user_id": user_id,
        "status": status,
    })
    await r.expire(token, token_live)


async def get_user_from_cache(token: str):
    return await r.json().get(token)


async def delete_user_cache(token: str):
    await r.json().delete(token)