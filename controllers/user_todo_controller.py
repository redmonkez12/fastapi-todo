from typing import Annotated

from fastapi import APIRouter, status, Body, Depends, HTTPException, Response, Query
from fastapi.responses import JSONResponse

from fastapi.encoders import jsonable_encoder
from auth.user import get_current_user
from deps import get_user_todo_service
from custom_exceptions import TodoDuplicationException
from responses import GetByUsernameResponse
from services.user_todo_service import UserTodoService
from requests import CreateTodoRequest, UpdateTodoRequest

user_todo_router = APIRouter(
    prefix="/users/todos",
    tags=["User todos"]
)


@user_todo_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(*, todo: CreateTodoRequest,
                      todo_service: UserTodoService = Depends(get_user_todo_service),
                      current_user: GetByUsernameResponse = Depends(get_current_user),
                      ):
    try:
        new_todo = await todo_service.create_todo(todo, current_user.user_id)
        created_at = new_todo.created_at
        todo_id = new_todo.id
        label = new_todo.label

        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content=jsonable_encoder(
                                {
                                    "todo_id": todo_id,
                                    "label": label,
                                    "created_at": created_at,
                                }
                            ))
    except TodoDuplicationException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "message": str(e),
            "code": "EMAIL_DUPLICATION",
            "status_code": status.HTTP_409_CONFLICT,
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "message": "Something went wrong",
            "code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        })


@user_todo_router.get("/")
async def get_todos(*,
                    todo_service: UserTodoService = Depends(get_user_todo_service),
                    offset: Annotated[int | None, Query()] = 0,
                    limit: Annotated[int | None, Query()] = 10,
                    current_user: GetByUsernameResponse = Depends(get_current_user),
                    ):
    todo = await todo_service.get_todos(current_user.user_id, offset, limit)

    return todo


@user_todo_router.get("/{todo_id}")
async def get_todo(*,
                   todo_id: int,
                   todo_service: UserTodoService = Depends(get_user_todo_service),
                   current_user: GetByUsernameResponse = Depends(get_current_user),
                   ):
    todo = await todo_service.get_todo(current_user.user_id, todo_id)

    return todo


@user_todo_router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(*,
                      todo: UpdateTodoRequest,
                      todo_service: UserTodoService = Depends(get_user_todo_service),
                      current_user: GetByUsernameResponse = Depends(get_current_user),
                      ):
    await todo_service.update_todo(current_user.user_id, todo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_todo_router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(*,
                      todo_id: int,
                      todo_service: UserTodoService = Depends(get_user_todo_service),
                      current_user: GetByUsernameResponse = Depends(get_current_user),
                      ):
    await todo_service.delete_todo(current_user.user_id, todo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
