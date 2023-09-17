from typing import List

from fastapi import APIRouter, Query, Depends, Path, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..db import db
from ..dependencies.functional import get_current_active_supervisor, get_current_active_guest
from ..schemas.order import TableListOrder, BaseWorkOrder, UpdateBySupervisorBaseWorkOrder, UpdateByGuestBaseWorkOrder
from ..schemas.user import User

router = APIRouter()
COLLECTION = 'orders'


@router.get('/find', response_model=TableListOrder)
async def find_orders(
        skip: int = Query(0, description="Skip documents"),
        limit: int = Query(10, description="Limit the number of documents to retrieve"),
        status: List[str] = Query(None, description="Filter by status"),
        order_type: List[str] = Query(None, description="Filter by order type"),
        room: List[str] = Query(None, description="Filter by room"),
):
    """
    The find orders in query condition below here:

    :param skip:
    :param limit:
    :param status:
    :param order_type:
    :param room:
    :return:
    """
    query = {}
    if status:
        query["status"] = {"$in": status}
    if order_type:
        query["type"] = {"$in": order_type}
    if room:
        query["room"] = {"$in": room}

    result = await db.find(collection=COLLECTION, query=query).skip(skip).limit(limit)
    orders = [order for order in result]
    return orders


@router.post('/create-supervisor', response_model=BaseWorkOrder, status_code=status.HTTP_201_CREATED)
async def create_work_order_by_supervisor(payload: BaseWorkOrder,
                                          current_user: User = Depends(get_current_active_supervisor)):
    """

    :param payload:
    :param current_user:
    :return:
    """

    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.put('/update-supervisor/{order_id}', response_model=UpdateBySupervisorBaseWorkOrder)
async def update_order_by_supervisor(payload: UpdateBySupervisorBaseWorkOrder,
                                     order_id: str = Path(title='update order in database-collection'),
                                     current_user: User = Depends(get_current_active_supervisor)):
    """

    :param payload:
    :param current_user:
    :return:
    """

    item_model = jsonable_encoder(payload)
    query = {'uid': order_id}
    values = {'$set': item_model}
    if (await db.update_one(
            collection=COLLECTION,
            query=query,
            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {order_id} or update already exits.')
    return item_model


@router.delete('/revoke/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def revoke_order(order_id: str = Path(title='delete order in database-collection'),
                       current_user: User = Depends(get_current_active_supervisor)):
    """

    :param order_id:
    :return:
    """

    if (await db.delete_one(collection=COLLECTION, query={'_id': order_id})) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"order is not found {order_id}."
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={'status': 'success'})


@router.post('/create-guest', response_model=BaseWorkOrder, status_code=status.HTTP_201_CREATED)
async def create_work_order_by_supervisor(payload: BaseWorkOrder,
                                          current_user: User = Depends(get_current_active_guest)):
    """

    :param payload:
    :param current_user:
    :return:
    """

    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.put('/update-guest/{order_id}', response_model=UpdateByGuestBaseWorkOrder)
async def update_order_by_supervisor(payload: UpdateByGuestBaseWorkOrder,
                                     order_id: str = Path(title='update order in database-collection'),
                                     current_user: User = Depends(get_current_active_guest)):
    """

    :param payload:
    :param current_user:
    :return:
    """

    item_model = jsonable_encoder(payload)
    query = {'uid': order_id}
    values = {'$set': item_model}
    if (await db.update_one(
            collection=COLLECTION,
            query=query,
            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {order_id} or update already exits.')
    return item_model
