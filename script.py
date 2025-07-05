from models.logsModel import ActionLog
from db.SQL_connection import SQL_connection
from sqlmodel import SQLModel

SQLModel.metadata.create_all(SQL_connection)