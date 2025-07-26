from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class CreateTask(BaseModel):
    title: str
    description: str | None
    status: TaskStatus


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str