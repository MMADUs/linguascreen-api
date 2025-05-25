from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session

from config import settings
from db import get_session

from models.user import User
from security.auth import get_user_by_id

# JWT bearer token security scheme
jwt_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    # copy data to encode
    to_encode = data.copy()
    # check if expiry are provided
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # set payload and generate token
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    # return token
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme),
    db: Session = Depends(get_session),
) -> User:
    """Get current user from JWT token"""
    # exception structure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # authenticate
    try:
        # extract token from credentials
        token = credentials.credentials
        # decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # extract user id as string
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # convert id string to integer
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # get the user by id
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    # return user data
    return user
