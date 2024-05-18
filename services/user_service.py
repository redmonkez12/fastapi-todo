from datetime import datetime

import asyncpg
from sqlmodel import Session, select
from sqlalchemy import exc

from password import hash_password, verify_password
from custom_exceptions import EmailDuplicationException, UserNotFoundException
from models.user import User
from requests import CreateUserRequest, LoginRequest


class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, data: CreateUserRequest):
        try:
            new_user = User(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                birthdate=datetime.strptime(data.birthdate, "%Y-%m-%d").date(),
                username=data.username,
                password=hash_password(data.password).decode("utf-8"),
            )

            self.session.add(new_user)
            await self.session.commit()

            return new_user
        except (exc.IntegrityError, asyncpg.exceptions.UniqueViolationError):
            raise EmailDuplicationException(f"Email [{data.email}] already exists")
        except Exception as e:
            raise Exception(e)

    async def get_by_username(self, username: str):
        query = (
            select(User.user_id, User.username, User.email, User.password)
            .where(User.username == username)
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.first()

    async def login(self, data: LoginRequest):
        user = await self.get_by_username(data.username)

        if not user:
            raise UserNotFoundException("Username or password is invalid")

        if not verify_password(data.password, user.password.encode("utf-8")):
            raise UserNotFoundException("Username or password is invalid")

        return user
