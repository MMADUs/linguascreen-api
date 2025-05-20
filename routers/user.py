from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from db import get_session
from models.user import User, RegisterSchema, UserResponse
from security.auth import get_password_hash
from security.jwt import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def register(req_body: RegisterSchema, db: Session = Depends(get_session)):
    """Create a new user with hashed password"""
    # Check if username already exists
    existing_user = db.exec(
        select(User).where(User.username == req_body.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = db.exec(select(User).where(User.email == req_body.email)).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(req_body.password)
    db_user = User(
        username=req_body.username,
        email=req_body.email,
        hashed_password=hashed_password,
    )

    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/auth", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_auth_session(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
