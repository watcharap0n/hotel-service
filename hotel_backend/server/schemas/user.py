from typing import Union, Optional

from pydantic import BaseModel


class User(BaseModel):
    uid: str
    username: str
    role: str
    position: Optional[str] = None
    disabled: Union[bool, None] = None
