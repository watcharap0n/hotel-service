from typing import Union, List

from pydantic import BaseModel

from ..schemas.employee import Employee
from ..schemas.guest import Guest


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class EmployeeInDB(Employee):
    hashedPassword: str


class GuestInDB(Guest):
    hashedPassword: str
