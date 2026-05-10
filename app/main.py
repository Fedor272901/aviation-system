from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_tables
from app.routers import person


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(person.router)


@app.get("/")
def root():
    return {"message": "hello"}
