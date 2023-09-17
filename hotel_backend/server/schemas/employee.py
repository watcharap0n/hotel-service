from datetime import datetime
from typing import Union, Optional, List
from uuid import uuid4

import pytz
from bson import ObjectId
from pydantic import BaseModel, Field, UUID4, validator

from ..db import PyObjectId


class RegisterEmployee(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    uid: UUID4 = Field(default_factory=uuid4)
    username: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-z0-9_.]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    hashedPassword: str
    firstname: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z]+$',
        description='Allow only alphabetic eng character'
    )
    lastname: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z]+$',
        description='Allow only alphabetic eng character'
    )
    nickname: Optional[str] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z ]+$',
        description='Allow only alphabetic eng character'
    )
    tel: str = Field(
        ...,
        regex='^\\+?[0-9][0-9]{7,14}$',
        description='Number tel.'
    )
    position: Optional[str] = None
    role: Optional[str] = 'employee'
    disabled: Union[bool, None] = False
    logged: Optional[bool] = False
    date: Union[datetime, None] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'username': 'dev',
                'hashedPassword': 'secret',
                'firstname': 'watcharapon',
                'lastname': 'weraborirak',
                'nickname': 'kane',
                'tel': '0941499661',
                'position': 'Technician',
                'role': 'supervisor',
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateEmployee(BaseModel):
    uid: str
    username: Optional[str] = None
    firstname: Optional[str] = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z]+$',
        description='Allow only alphabetic eng character'
    )
    lastname: Optional[str] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z]+$',
        description='Allow only alphabetic eng character'
    )
    nickname: Optional[str] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z ]+$',
        description='Allow only alphabetic eng character'
    )
    tel: Optional[str] = Field(
        None,
        regex='^\\+?[0-9][0-9]{7,14}$',
        description='Number tel.'
    )
    position: Optional[str] = None
    role: Optional[str] = None
    disabled: Union[bool, None] = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'username': 'dev',
                'hashedPassword': 'secret',
                'firstname': 'watcharapon',
                'lastname': 'weraborirak',
                'nickname': 'kane',
                'tel': '0941499661',
                'position': 'Technician',
                'role': 'supervisor',
            }
        }


class Employee(BaseModel):
    uid: str
    username: str
    firstname: Union[str, None] = None
    lastname: Union[str, None] = None
    nickname: Union[str, None] = None
    position: Optional[str] = None
    role: str
    logged: bool
    disabled: Union[bool, None] = None


class TableListEmployee(BaseModel):
    counts: int
    skip: int
    limit: int
    employees: Union[List[Employee], None] = []
