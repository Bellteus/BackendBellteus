from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    role: str
    is_active: bool = True
    created_at: datetime = datetime.now()