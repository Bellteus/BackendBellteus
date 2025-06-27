from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserPublic(BaseModel):
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime = None  # Optional, can be set later if needed

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    is_active: bool = True

class UserCreateResponse(BaseModel):
    message: str
    data: UserPublic

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
