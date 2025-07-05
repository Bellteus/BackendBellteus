from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ActionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    user_email: str
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)