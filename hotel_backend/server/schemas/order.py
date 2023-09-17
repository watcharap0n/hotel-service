from datetime import datetime
from typing import Union, List

import pytz
from bson import ObjectId
from pydantic import BaseModel, Field, validator

from ..db import PyObjectId
from ..routes.employee import Employee


class BaseWorkOrder(BaseModel):
    workOrderNumber: str
    createBy: Employee
    assignedTo: Employee
    numberRoom: str
    started: datetime
    finished: datetime
    type: str
    status: str
    date: Union[datetime, None] = None


class TableListOrder(BaseModel):
    counts: int
    skip: int
    limit: int
    guests: Union[List[BaseWorkOrder], None] = []


class CreateBaseWorkOrder(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    workOrderNumber: str
    createBy: Employee
    assignedTo: Employee
    numberRoom: str
    started: datetime
    finished: datetime
    type: str
    status: str
    date: Union[datetime, None] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'workOrderNumber': '20230913-0933-101',
                'createBy': {},
                'assignedTo': {},
                'numberRoom': '101',
                'started': '2023-08-10T10:00',
                'finished': '2023-08-10T11:00',
                'type': 'Technician Request',
                'status': 'Done'
            }
        }

    @validator('workOrderNumber', pre=True, always=True)
    def set_work_order_number(cls, work_order_number, values):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return f'{dt.year}{dt.month:02d}{dt.day:02d}-{dt.hour:02d}{dt.min:02d}-{values["numberRoom"]}'

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateBySupervisorBaseWorkOrder(BaseModel):
    workOrderNumber: str
    assignedTo: Employee
    numberRoom: str
    started: datetime
    finished: datetime
    type: str
    status: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'workOrderNumber': '20230913-0933-101',
                'assignedTo': {},
                'numberRoom': '101',
                'started': '2023-08-10T10:00',
                'finished': '2023-08-10T11:00',
                'type': 'Technician Request',
                'status': 'Done'
            }
        }


class UpdateByGuestBaseWorkOrder(BaseModel):
    status: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'status': 'Done'
            }
        }
