from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ActionLog(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    user_email: str
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)