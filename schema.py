from pydantic import BaseModel, Field,  EmailStr
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str
    published: bool = Field(default=True)

class PostUpdate(PostCreate):
    pass



class PostResponse(PostCreate):
    id: int
    user_id: int
    created_at: datetime
    owner: Optional['UserResponse']  # Forward reference
    class Config:
        orm_mode = True




class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(UserCreate):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


class LikeRequest(BaseModel):
    post_id: int
    direction: int  # 1 = like, 0 = unlike