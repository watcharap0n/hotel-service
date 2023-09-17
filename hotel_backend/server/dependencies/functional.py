from fastapi import Security, status, HTTPException, Depends

from ..routes.auth import get_current_user
from ..schemas.employee import Employee
from ..schemas.guest import Guest
from ..schemas.user import User


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
