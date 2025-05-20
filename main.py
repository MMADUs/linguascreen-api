from fastapi import FastAPI

from config import settings
from db import create_db_and_tables
from routers import auth, user, words

# Create FastAPI app
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(words.router)


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
