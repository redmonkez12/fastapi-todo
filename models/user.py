import datetime

from sqlmodel import SQLModel, Field, Relationship

import sqlalchemy as sa


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False, unique=True))
    first_name: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False))
    last_name: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False))
    email: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False, unique=True))
    birthdate: datetime.date = Field(nullable=False)
    password: str = Field(sa_column=sa.Column(sa.TEXT, nullable=False))
    created_at: str = Field(sa_column=sa.Column(sa.DateTime(timezone=True), default=datetime.datetime.now))

    todos: list["Todo"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'joined'})
