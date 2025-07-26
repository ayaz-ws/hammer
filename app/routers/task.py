from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select
from slugify import slugify

from app.backend.depends import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas import CreateTask

from app.routers.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["task"])


@router.get("/")
async def get_all_tasks(
    db: Annotated[Session, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    sort: TaskStatus,
):
    user_id = get_user.get("id")
    is_admin = get_user.get("is_admin")
    # Админ получает задачи всех пользователей
    if is_admin == True:
        tasks = await db.scalars(
            select(Task).where(Task.status == sort)
        )
    # Если обычный пользователь, то получит только свои задачи
    else:
        tasks = await db.scalars(
            select(Task).where(Task.user_id == user_id, Task.status == sort)
        )
    tasks = tasks.all()
    # Проверка на наличие или отсутствие задач
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found"
        )
    return


@router.post("/")
async def create_task(
    db: Annotated[Session, Depends(get_db)],
    create_task: CreateTask,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    user_id = get_user.get("id")
    await db.execute(
        insert(Task).values(
            title=create_task.title,
            description=create_task.description,
            status=create_task.status,
            user_id=user_id,
        )
    )
    await db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "The task has created successfully",
    }


@router.put("/{task_id}")
async def update_task(
    db: Annotated[Session, Depends(get_db)],
    create_task: CreateTask,
    get_user: Annotated[dict, Depends(get_current_user)],
    task_id: int,
):
    user_id = get_user.get("id")
    is_admin = get_user.get("is_admin")
    task = await db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    # Задачи изменять может только админ или автор этой задачи
    if task.user_id == user_id or is_admin == True:
        task.title = create_task.title
        task.description = create_task.description
        task.status = create_task.status
        await db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "The task has updated successfully",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@router.delete("/{task_id}")
async def delete_task(
    db: Annotated[Session, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    task_id: int,
):
    user_id = get_user.get("id")
    is_admin = get_user.get("is_admin")
    task = await db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    # Удалять задачу может только админ и автор задачи
    if task.user_id == user_id or is_admin == True:
        await db.delete(task)
        await db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Deleted successfully",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
