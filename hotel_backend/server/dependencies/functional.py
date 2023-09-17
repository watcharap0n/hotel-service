import os
from typing import Union

from fastapi import HTTPException, Header, status


async def x_api_token_authorize(x_api_token: Union[str, None] = Header(default=None)):
    if not x_api_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='X-API-TOKEN header is bad request.')
    if x_api_token != os.getenv('X_API_TOKEN', None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='X-API-TOKEN header invalid')
