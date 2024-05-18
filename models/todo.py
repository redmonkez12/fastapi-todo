import datetime

from sqlmodel import SQLModel, Field, Relationship

import sqlalchemy as sa

from models.user import User


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    label: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False, unique=True))
    user_id: int = Field(
        sa_column=sa.Column(sa.Integer, sa.ForeignKey(User.user_id, ondelete="CASCADE"), nullable=False))
    created_at: datetime.datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)))

    user: User = Relationship(back_populates="todos")

