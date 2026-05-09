import sys, os

sys.path.append(os.path.dirname(__file__))
from fastapi import FastAPI
from app.routers import person

app = FastAPI()

# include routers
app.include_router(person.router)


@app.get("/")
def root():
    return {"message": "hello"}
