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
