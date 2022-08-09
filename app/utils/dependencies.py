import re

from fastapi import Depends, HTTPException, status
from fastapi_users.db import OrmarUserDatabase

from app.models.user import UserDB, UserModel
from app.db.managers import UserManager
from app.datasources.internal.bdx_am import BdxAm



def get_user_db():
    yield OrmarUserDatabase(UserDB, UserModel)


def get_user_manager(user_db: OrmarUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_current_user():
    from app.routers.users import fastapi_users
    return fastapi_users.current_user(active=True)


def get_current_admin():
    from app.routers.users import fastapi_users
    return fastapi_users.current_user(superuser=True)


async def get_eans(query: str):
    query = re.findall(r'(\d+)', query)
    # Pad old ean that are not up to 13 digits
    query = [ean.zfill(13) if len(ean)>8 and len(ean)<13 else ean for ean in query]
    query_items_length = set(len(num) for num in query)
    if not query_items_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty query",
            )
    if len(query_items_length) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mixed length items in query",
            )
    if query_items_length.pop() not in (13, ):
        pim_client = BdxAm()
        eans = list()
        for num in query:
            ean = await pim_client.pim2ean(query=num)
            ean and eans.append(ean)
        if not eans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid PIM_SKU found in query",
                )
        query = eans
    return query
