from fastapi import APIRouter, Depends
from sqlalchemy import select

from auth.dependencies import current_user_dependency
from db.session import async_session
from db import models as db_models
from db.crud import get_or_create_user
from .schemas import UserOut


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current=Depends(current_user_dependency)) -> UserOut:
    stytch_user_id = current.user_id
    email = current.email
    name = getattr(current, "name", None)

    async with async_session() as session:
        result = await session.execute(
            select(db_models.User).where(db_models.User.stytch_user_id == stytch_user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            user = await get_or_create_user(
                session,
                stytch_user_id=stytch_user_id,
                email=email,
                name=name,
            )
        return UserOut.model_validate(user)

