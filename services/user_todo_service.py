import asyncpg
from sqlalchemy import exc
from sqlmodel import select, and_, delete, update, Session

from custom_exceptions import TodoDuplicationException
from models.todo import Todo
from models.user import User
from requests import CreateTodoRequest, UpdateTodoRequest


class UserTodoService:
    def __init__(self, session: Session):
        self.session = session

    async def create_todo(self, data: CreateTodoRequest, user_id: int):
        try:
            new_todo = Todo(label=data.label, user_id=user_id)

            self.session.add(new_todo)
            await self.session.commit()

            return new_todo
        except (exc.IntegrityError, asyncpg.exceptions.UniqueViolationError):
            raise TodoDuplicationException(f"Todo [{data.label}] already exists")
        except Exception as e:
            raise Exception(e)

    async def get_todos(self, user_id: int, offset: int, limit: int):
        query = (
            select(Todo)
            .where(Todo.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_todo(self, user_id: int, todo_id: int):
        query = (
            select(Todo)
            .where(and_(Todo.user_id == user_id, Todo.id == todo_id))
        )

        result = await self.session.execute(query)
        return result.scalars().one()

    async def delete_todo(self, user_id: int, todo_id: int) -> None:
        query = (
            delete(Todo)
            .where(and_(Todo.id == todo_id, User.user_id == user_id))
        )

        await self.session.execute(query)
        await self.session.commit()

    async def update_todo(self, user_id: int, new_todo: UpdateTodoRequest) -> None:
        query = (
            update(Todo)
            .values(label=new_todo.label)
            .where(and_(Todo.id == new_todo.id, User.user_id == user_id))
        )

        await self.session.execute(query)
        await self.session.commit()