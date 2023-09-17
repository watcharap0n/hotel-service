from typing import Union

from fastapi import APIRouter, Query, HTTPException, Depends, Path, status
from fastapi.encoders import jsonable_encoder

from .auth import get_current_active_supervisor
from ..db import db
from ..schemas.guest import RegisterGuest, TableListGuest, Guest, UpdateGuest

router = APIRouter()
COLLECTION = 'users'


async def evaluate_duplicate_account(register: RegisterGuest):
    if await db.find_one(collection=COLLECTION, query={'username': register.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    return register


async def evaluate_duplicate_account_update(model: UpdateGuest):
    if user := await db.find_one(collection=COLLECTION, query={'username': model.username}):
        if user['uid'] == model.uid:
            return model
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    if user := await db.find_one(collection=COLLECTION, query={'numberRoom': model.numberRoom}):
        if user['uid'] == model.uid:
            return model
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='numberRoom already exist.')
    return model


@router.get('/find/guest', response_model=TableListGuest)
async def read_users(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start items in collection', ge=0),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end items in collection', ge=1),
        current_user: Guest = Depends(get_current_active_supervisor),
):
    total_count = db.get_collection_countable(collection=COLLECTION, query={'role': 'guest'})
    users = await db.find(collection=COLLECTION, query={'role': 'guest'})
    stored_model = users.skip(skip).limit(limit)
    stored_model = list(stored_model)
    result = {
        'counts': total_count,
        'skip': skip,
        'limit': limit,
        'guests': stored_model
    }
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return result


@router.post('/create/guest', response_model=RegisterGuest)
async def register_user(
        register: RegisterGuest = Depends(evaluate_duplicate_account),
        current_user: Guest = Depends(get_current_active_supervisor)
):
    item_model = jsonable_encoder(register)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.put('/update/guest/{uid}', response_model=UpdateGuest)
async def update_user(
        user: UpdateGuest = Depends(evaluate_duplicate_account_update),
        uid: str = Path(title='User UID in database-collection for update user'),
        current_user: Guest = Depends(get_current_active_supervisor),
):
    item_model = jsonable_encoder(user)
    query = {'uid': uid}
    values = {'$set': item_model}
    if (await db.update_one(
            collection=COLLECTION,
            query=query,
            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {uid} or update already exits.')
    return item_model
