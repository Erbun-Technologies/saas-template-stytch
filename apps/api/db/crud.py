from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from . import models


async def get_or_create_user(
    session: AsyncSession,
    *,
    stytch_user_id: str,
    email: str,
    name: Optional[str] = None,
) -> models.User:
    """Get by Stytch user id; create if missing. Update last_login on access."""
    result = await session.execute(
        select(models.User).where(models.User.stytch_user_id == stytch_user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        # Update fields if changed and bump last_login
        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if name is not None and user.name != name:
            user.name = name
            updated = True
        user.last_login = func.now()
        await session.commit()
        if updated:
            await session.refresh(user)
        return user

    # Create new user
    user = models.User(
        stytch_user_id=stytch_user_id,
        email=email,
        name=name,
        last_login=func.now(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

