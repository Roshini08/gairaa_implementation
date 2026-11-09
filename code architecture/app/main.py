from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="BugWise AI",
    description="AI-Powered Bug Classification and Prioritization API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "message": "Welcome to BugWise AI",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "SQLite"
    }


app.include_router(router, prefix="/api/v1")








