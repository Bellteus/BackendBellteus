from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserInDB(BaseModel):
    id: str = Field(alias="_id")  # <- convierte automáticamente ObjectId a id
    email: EmailStr
    hashed_password: str
    role: str
    is_active: bool = True
    created_at: datetime = datetime.now()

class UserPublic(BaseModel):
    id: str  # Aquí el ObjectId como string
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
