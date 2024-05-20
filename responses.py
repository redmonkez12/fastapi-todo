from pydantic import BaseModel


class GetByUsernameResponse(BaseModel):
    user_id: int
    username: str
    email: str
    password: str
