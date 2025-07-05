# db/SQL_connection.py
from dotenv import load_dotenv
load_dotenv()

import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("LOGS_DB_URL")
if not DATABASE_URL:
    raise RuntimeError("LOGS_DB_URL no está definida en variables de entorno")

engine = create_engine(DATABASE_URL, echo=False)
SQL_connection = engine

def get_session():
    with Session(engine) as session:
        yield session
