from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from typing import List
from config.mongodb import get_mongo_client
from models.logsModel import ActionLog
from db.SQL_connection import get_session   # <-- Usa tu función, no la de huggingface

router = APIRouter()

mongo = get_mongo_client()
logs_collection = mongo["CALLCENTER-MONGODB"]["logs"]

@router.get("/logs", response_model=List[ActionLog])
def get_logs():
    logs = []
    for log in logs_collection.find().sort("timestamp", -1):
        log["_id"] = str(log["_id"])
        logs.append(ActionLog(**log))
    return logs

@router.post("/logs", response_model=ActionLog, status_code=status.HTTP_201_CREATED)
def create_log(log: ActionLog):
    log_dict = log.dict(by_alias=True, exclude_unset=True)
    log_dict["timestamp"] = datetime.utcnow()
    result = logs_collection.insert_one(log_dict)
    log_dict["_id"] = str(result.inserted_id)
    print(f"[LOG SUCCESS] Nuevo log registrado: {log_dict}")  # <-- Mensaje en consola
    return ActionLog(**log_dict)