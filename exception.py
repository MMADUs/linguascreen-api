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

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from azure.core.exceptions import HttpResponseError

from main import app


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Custom error exception for database error"""
    # throw error
    print(f"Database error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"},
    )


@app.exception_handler(HttpResponseError)
async def http_response_error_handler(request: Request, exc: HttpResponseError):
    """Custom error exception for azure client"""
    # throw error
    print(f"HttpResponseError on {request.url}: {exc}")
    detail = exc.message if hasattr(exc, "message") else str(exc)
    return JSONResponse(
        status_code=502,
        content={"detail": f"External service error: {detail}"},
    )
