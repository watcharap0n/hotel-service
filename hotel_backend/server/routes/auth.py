import os
from datetime import datetime, timedelta
from typing import Union

from fastapi import (APIRouter, HTTPException, status, Depends, Security)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from ..db import db
from ..schemas.auth import EmployeeInDB, GuestInDB, TokenData, Token
from ..schemas.employee import Employee
from ..schemas.guest import Guest
from ..schemas.user import User

SECOND = 60
MINUTE = os.environ.get('EXPIRES_TOKEN', '60')
EXPIRES_TOKEN = SECOND * int(MINUTE) * 24
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
COLLECTION = 'users'

authenticate = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token',
                                     scopes={
                                         'me': 'Read information about the current user.',
                                         'supervisor': 'Read information apis for supervisor.',
                                         'employee': 'Read information apis for employee.',
                                         'guest': 'Read information apis for guest.'
                                     })


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    user_db = await db.find_one(collection=COLLECTION, query={'username': username})
    if user_db:
        if user_db['role'] == 'guest':
            return GuestInDB(**user_db)
        return EmployeeInDB(**user_db)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid username or not register.')
    if not verify_password(password, user.hashedPassword):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid password please try again.')
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_scopes = payload.get('scopes', [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not enough permissions',
        headers={'WWW-Authenticate': authenticate_value},
    )


async def get_current_active_supervisor(
        current_user: Employee = Security(get_current_user, scopes=['me', 'supervisor'])
):
    """
    inactive user config this here:
        - disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    if current_user.role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    if current_user.role != 'supervisor':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not enough permissions')
    return current_user


async def get_current_active_employee(
        current_user: Employee = Security(get_current_user, scopes=['me', 'employee'])
):
    """
    inactive user config this here:
        - disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    if current_user.role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    if current_user.role != 'supervisor' or current_user.role != 'employee':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not enough permissions')
    return current_user


async def get_current_active_guest(
        current_user: Guest = Security(get_current_user, scopes=['me', 'guest'])
):
    """
    inactive user config this here:
        - disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    if current_user.role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    if current_user.role != 'guest':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not enough permissions')
    return current_user


async def get_current_active_group(
        current_user: User = Security(get_current_user, scopes=['me', 'supervisor', 'employee', 'guest'])
):
    """
    inactive user config this here:
        - disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    if current_user.role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    return current_user


def has_scope(required_role: str = Depends(get_current_user)):
    def _has_scope(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient scope")
        return user

    return _has_scope


@authenticate.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if user.role == 'admin':
        access_token_expires = timedelta(seconds=EXPIRES_TOKEN)
        access_token = create_access_token(
            data={'sub': user.username, 'scopes': form_data.scopes},
            expires_delta=access_token_expires
        )
        return {'access_token': access_token, 'token_type': 'bearer'}

    if user.role not in form_data.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not enough permissions.')
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect username or password')
    access_token_expires = timedelta(seconds=EXPIRES_TOKEN)
    access_token = create_access_token(
        data={'sub': user.username, 'scopes': form_data.scopes},
        expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@authenticate.get('/user/me/', response_model=User)
async def read_user_me(current_user: User = Depends(get_current_active_group)):
    return current_user


@authenticate.get('/status/')
async def read_system_status(current_user: User = Depends(get_current_user)):
    return {'status': True, 'service': 'Hotel service'}
