from typing import Union

from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder

from ..db import db
from ..dependencies.functional import get_current_active_supervisor
from ..routes.auth import get_password_hash
from ..schemas.guest import RegisterGuest, TableListGuest, Guest

router = APIRouter()
COLLECTION = 'users'


async def evaluate_duplicate_account(register: RegisterGuest):
    if await db.find_one(collection=COLLECTION, query={'username': register.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    return register


@router.get('/find/guest', response_model=TableListGuest)
async def read_users(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start items in collection', ge=0),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end items in collection', ge=1),
        current_user: Guest = Depends(get_current_active_supervisor),
):
    total_count = db.get_collection_countable(collection=COLLECTION)
    users = await db.find(collection=COLLECTION, query={})
    stored_model = users.skip(skip).limit(limit)
    stored_model = list(stored_model)
    result = {
        'counts': total_count,
        'skip': skip,
        'limit': limit,
        'users': stored_model
    }
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return result


@router.post('/create/guest', response_model=Guest)
async def register_user(
        register: RegisterGuest = Depends(evaluate_duplicate_account),
        current_user: Guest = Depends(get_current_active_supervisor)
):
    hashed = get_password_hash(register.hashed_password)
    register.hashed_password = hashed
    item_model = jsonable_encoder(register)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model
