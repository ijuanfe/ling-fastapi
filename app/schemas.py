# pydantic is a module that force the client to send the data in a schema
# and automatically validates the data types in the body request
from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr  # validate email format
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str
    is_published: bool = True  # default value
    # rating: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserOut

    class Config:  # Allows to convert from ORM (SQLAlchemy model) to Pydantic model to validate the data
        orm_mode = True


class PostOut(BaseModel):
    Post: PostResponse
    votes: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
