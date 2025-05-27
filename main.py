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

from fastapi import FastAPI

from config import settings
from db import create_db_and_tables
from routers import auth, sentences, gateway

# main app
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# add routers
app.include_router(auth.router)
app.include_router(sentences.router)
app.include_router(gateway.router)


@app.on_event("startup")
def on_startup():
    """Initialize database on application startup"""
    create_db_and_tables()


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": f"{settings.APP_NAME} is running!"}


# For running the application directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
