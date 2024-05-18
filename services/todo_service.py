from sqlalchemy import delete, update
from sqlmodel import Session, select
from models.todo import Todo
from requests import CreateTodoRequest, UpdateTodoRequest


class TodoService:
    def __init__(self, session: Session):
        self.session = session

    async def create_todo(self, data: CreateTodoRequest):
        new_todo = Todo(label=data.label)

        self.session.add(new_todo)
        await self.session.commit()

        return new_todo

    async def get_todo(self, todo_id: int) -> Todo:
        query = (
            select(Todo)
            .where(Todo.id == todo_id)
        )

        result = await self.session.execute(query)

        return result.scalars().one()

    async def get_todos(self, offset: int, limit: int) -> list[Todo]:
        query = (
            select(Todo)
            .offset(offset)
            .limit(limit)
        )

        data = await self.session.execute(query)
        return data.scalars().all()

    async def update_todo(self, new_todo: UpdateTodoRequest) -> None:
        query = (
            update(Todo)
            .values(label=new_todo.label)
            .where(Todo.id == new_todo.id)
        )

        await self.session.execute(query)
        await self.session.commit()

    async def delete_todo(self, todo_id: int) -> None:
        query = (
            delete(Todo)
            .where(Todo.id == todo_id)
        )

        await self.session.execute(query)
        await self.session.commit()
