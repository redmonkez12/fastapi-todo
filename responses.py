from pydantic import BaseModel


class GetByUsernameResponse(BaseModel):
    user_id: str
    username: str
    email: str
    password: str
