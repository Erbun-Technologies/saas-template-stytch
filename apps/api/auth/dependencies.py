from fastapi import Depends, Request

from .service import get_current_user


async def current_user_dependency(request: Request):
    return await get_current_user(request)
