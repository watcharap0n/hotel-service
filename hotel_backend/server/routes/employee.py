from typing import Union, List

from fastapi import APIRouter, Query, HTTPException, Depends, status, Path
from fastapi.encoders import jsonable_encoder

from ..db import db
from ..routes.auth import get_current_active_employee
from ..schemas.employee import RegisterEmployee, UpdateEmployee, TableListEmployee, Employee

router = APIRouter()
COLLECTION = 'users'


async def evaluate_duplicate_account(register: RegisterEmployee):
    if await db.find_one(collection=COLLECTION, query={'username': register.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    return register


async def evaluate_duplicate_account_update(model: UpdateEmployee):
    if user := await db.find_one(collection=COLLECTION, query={'username': model.username}):
        if user['uid'] == model.uid:
            return model
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    return model


@router.get('/find/employee', response_model=TableListEmployee)
async def read_users(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start items in collection', ge=0),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end items in collection', ge=1),
        position: List[str] = Query(None, description="Filter by position"),
        role: List[str] = Query(None, description="Filter by role"),
        current_user: Employee = Depends(get_current_active_employee),
):
    """
    find employee following condition below

    :param skip:
    :param limit:
    :param position:
    :param role:
    :param current_user:
    :return:
    """
    query = {}
    total_count = db.get_collection_countable(collection=COLLECTION)
    if position:
        query["position"] = {"$in": position}
    if role:
        query["type"] = {"$in": role}

    users = await db.find(collection=COLLECTION, query=query)
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


@router.put('/update/employee/{uid}', response_model=UpdateEmployee)
async def update_user(
        user: UpdateEmployee = Depends(evaluate_duplicate_account_update),
        uid: str = Path(title='User UID in database-collection for update user'),
        current_user: Employee = Depends(get_current_active_employee),
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
