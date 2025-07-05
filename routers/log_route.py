from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from typing import List
from models.logsModel import ActionLog
from db.SQL_connection import get_session   # <-- Usa tu función, no la de huggingface

router = APIRouter()

@router.get("/logs", response_model=List[ActionLog])
def get_logs(session: Session = Depends(get_session)):
    logs = session.exec(select(ActionLog).order_by(ActionLog.timestamp.desc())).all()
    return logs

@router.post("/logs", response_model=ActionLog, status_code=status.HTTP_201_CREATED)
def create_log(log: ActionLog, session: Session = Depends(get_session)):
    log.timestamp = datetime.utcnow()
    session.add(log)
    session.commit()
    session.refresh(log)
    return log