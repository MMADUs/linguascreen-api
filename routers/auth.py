# Copyright (c) 2024-2025 LinguaScreen, Inc.
#
# This file is part of LinguaScreen Server
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from config import settings
from db import get_session

from models.user import User, RegisterSchema, RegisterResponse, LoginSchema, LoginResponse

from security.auth import authenticate_user, get_password_hash
from security.jwt import create_access_token, get_current_user

router = APIRouter(tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
def register(req_body: RegisterSchema, db: Session = Depends(get_session)):
    """Create a new user with hashed password"""
    # get user by email
    existing_user = db.exec(select(User).where(User.email == req_body.email)).first()
    # check if exist
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # hash password
    hashed_password = get_password_hash(req_body.password)
    # save to db
    db_user = User(
        username=req_body.username,
        email=req_body.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # return response
    return {
        "message": "successful account registration",
        "result": {
            "username": req_body.username,
            "email": req_body.email,
        },
    }


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(req_body: LoginSchema, db: Session = Depends(get_session)):
    """Endpoint for user authentication and token generation"""
    # authenticate user credential
    user = authenticate_user(db, req_body.email, req_body.password)
    # if credential does not match
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    # generate access token for session
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # return response
    return {
        "message": "successful login",
        "result": {
            "access_token": access_token,
            "token_type": "Bearer",
        },
    }


@router.get("/auth", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def get_auth_session(user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "message": "session authenticated",
        "result": {
            "username": user.username,
            "email": user.email,
        },
    }
