import json

from fastapi import FastAPI, status, HTTPException, Response, Depends

from database import init_db
from deps import get_todo_service, get_user_service
from custom_exceptions import EmailDuplicationException, UserNotFoundException
from models.todo import Todo
from requests import UpdateTodoRequest, CreateTodoRequest, CreateUserRequest, LoginRequest
from responses import GetByUsernameResponse
from services.todo_service import TodoService
from services.user_service import UserService
from jwt_token import create_access_token
from user import get_current_user

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db(False)


from sqlalchemy.exc import NoResultFound


@app.get("/")
def index():
    return "App is running"

@app.post("/todos", response_model=Todo)
async def create_todo(*, data: CreateTodoRequest, todo_service: TodoService = Depends(get_todo_service)):
    return await todo_service.create_todo(data)


@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(*,
                   todo_service: TodoService = Depends(get_todo_service),
                   todo_id: int
                   ):
    try:
        return await todo_service.get_todo(todo_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={
                                "message": f"Todo [{todo_id}] not found",
                                "status_code": status.HTTP_404_NOT_FOUND,
                                "code": "TODO_NOT_FOUND",
                            })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={
                                "message": "Something went wrong",
                                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                                "code": "INTERNAL_SERVER_ERROR",
                            })


@app.get("/todos", response_model=list[Todo])
async def get_todos(*,
                    todo_service: TodoService = Depends(get_todo_service),
                    offset: int | None = 0,
                    limit: int | None = 10,
                    current_user: GetByUsernameResponse = Depends(get_current_user),
                    ):
    print(current_user)  # we will use it later

    return await todo_service.get_todos(offset, limit)


@app.patch("/todos", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(*, todo: UpdateTodoRequest, todo_service: TodoService = Depends(get_todo_service)):
    found = await todo_service.get_todo(todo.id)

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={
                                "message": f"Todo [{todo.id}] not found",
                                "status_code": status.HTTP_404_NOT_FOUND,
                                "code": "TODO_NOT_FOUND",
                            })

    await todo_service.update_todo(todo)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(*, todo_id: int, todo_service: TodoService = Depends(get_todo_service)):
    found = await todo_service.get_todo(todo_id)

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={
                                "message": f"Todo [{todo_id}] not found",
                                "status_code": status.HTTP_404_NOT_FOUND,
                                "code": "TODO_NOT_FOUND",
                            })

    await todo_service.delete_todo(todo_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/login")
async def login(*, user_service: UserService = Depends(get_user_service),
                request: LoginRequest):
    try:
        user = await user_service.login(request)

        access_token = create_access_token(
            data={"sub": user.username}
        )

        return Response(status_code=status.HTTP_200_OK,
                        content=json.dumps({"access_token": access_token, "token_type": "bearer"}))
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password or username")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "message": "Something went wrong",
            "code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        })


@app.post("/users", response_class=Response, status_code=status.HTTP_201_CREATED)
async def create_user(*, user_service: UserService = Depends(get_user_service),
                      request: CreateUserRequest):
    try:
        await user_service.create_user(request)
        return Response(status_code=status.HTTP_201_CREATED)
    except EmailDuplicationException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "message": str(e),
            "code": "EMAIL_DUPLICATION",
            "status_code": status.HTTP_409_CONFLICT,
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "message": "Something went wrong",
            "code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        })
