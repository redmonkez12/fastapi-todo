from services.todo_service import TodoService
from database import async_session
from services.user_service import UserService


async def get_todo_service():
    async with async_session() as session:
        async with session.begin():
            yield TodoService(session)


async def get_user_service():
    async with async_session() as session:
        async with session.begin():
            yield UserService(session)
