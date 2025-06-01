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


class LoginResponse(BaseModel):
    """Response model for user login"""

    class TokenModel(BaseModel):
        """Token result model for login response"""

        access_token: str
        token_type: str = "Bearer"
        
    message: str
    result: TokenModel

class RegisterSchema(UserBase):
    """Schema for user creation"""

    password: str

class RegisterResponse(BaseModel):
    """Response model for user registration"""

    message: str
    result: UserBase

class AuthResponse(BaseModel):
    """Response model for user authentication"""

    message: str
    result: UserBase