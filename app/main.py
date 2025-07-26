from fastapi import FastAPI

from app.routers import task
from app.routers import auth


app = FastAPI()

app.include_router(task.router)
app.include_router(auth.router)