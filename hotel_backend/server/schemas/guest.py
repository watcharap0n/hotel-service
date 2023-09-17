from datetime import datetime
from typing import Union, Optional, List
from uuid import uuid4

import pytz
from bson import ObjectId
from pydantic import BaseModel, Field, UUID4, validator

from ..db import PyObjectId


class RegisterGuest(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    uid: UUID4 = Field(default_factory=uuid4)
    username: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-z0-9_.]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    hashedPassword: str
    numberRoom: str
    role: Optional[str] = 'Guest'
    logged: Optional[bool] = False
    date: Union[datetime, None] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'username': '101',
                'numberRoom': '101',
                'hashedPassword': 'secret',
                'role': 'supervisor',
            }
        }

    @validator('numberRoom')
    def set_duplicate_field_number(cls, number_room, values):
        username = values['username']
        return username

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class Guest(BaseModel):
    uid: str
    username: str
    numberRoom: str
    role: str
    logged: bool
    disabled: Union[bool, None] = None


class TableListGuest(BaseModel):
    counts: int
    skip: int
    limit: int
    guests: Union[List[Guest], None] = []
