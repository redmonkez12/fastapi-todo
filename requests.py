from pydantic import BaseModel


class CreateTodoRequest(BaseModel):
    label: str


class UpdateTodoRequest(BaseModel):
    id: int
    label: str


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    birthdate: str
    username: str
    password: str
