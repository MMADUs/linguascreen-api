from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from config import settings
from db import get_session
from models.user import UserCredential, LoginSchema
from security.auth import authenticate_user
from security.jwt import create_access_token

router = APIRouter(tags=["authentication"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserCredential)
async def login(req_body: LoginSchema, db: Session = Depends(get_session)):
    """Endpoint for user authentication and token generation"""
    # Authenticate the user
    user = authenticate_user(db, req_body.email, req_body.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
