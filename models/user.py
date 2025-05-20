from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class UserBase(SQLModel):
    """Base model for user data"""

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)


class User(UserBase, table=True):
    """Database model for users"""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


# User schema
class LoginSchema(BaseModel):
    """Schema for user login"""

    email: str
    password: str


class RegisterSchema(UserBase):
    """Schema for user creation"""

    password: str


class UserResponse(UserBase):
    """Schema for user response"""

    id: int


# Auth schema
class UserCredential(BaseModel):
    """Schema for token response"""

    access_token: str
    token_type: str
