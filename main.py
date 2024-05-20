from fastapi import FastAPI

from controllers.auth_controller import auth_router
from controllers.todo_controller import todo_router
from controllers.user_todo_controller import user_todo_router
from database import init_db

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db(False)


@app.get("/")
def index():
    return "App is running"


app.include_router(auth_router, prefix="/api/v1")
app.include_router(todo_router, prefix="/api/v1")
app.include_router(user_todo_router, prefix="/api/v1")
