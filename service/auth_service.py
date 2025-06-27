from config.mongodb import get_mongo_client
from config.security import hash_password, verify_password
from models.userModel import UserInDB
from schemas.userSchema import UserCreate, UserLogin, UserPublic
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

mongo = get_mongo_client()
user_collection = mongo["CALLCENTER-MONGODB"]["users"]

def get_user(email: str) -> Optional[UserInDB]:
    user_db = user_collection.find_one({"email": email})
    if user_db:
        return UserInDB(**user_db)
    return None

def create_user(user_create: UserCreate) -> UserPublic:
    if get_user(user_create.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usuario ya existe")

    hashed_password = hash_password(user_create.password)

    user_in_db = UserInDB(
        email=user_create.email,
        hashed_password=hashed_password,
        role=user_create.role,
        is_active=user_create.is_active,
        created_at=datetime.now()
    )

    user_collection.insert_one(user_in_db.dict())

    return UserPublic(
        email=user_create.email,
        role=user_create.role,
        is_active=user_create.is_active,
        created_at=user_in_db.created_at
    )

def authenticate_user(user_login: UserLogin) -> Optional[UserPublic]:
    user_db = get_user(user_login.email)
    if not user_db or not verify_password(user_login.password, user_db.hashed_password):
        return None

    return UserPublic(
        email=user_db.email,
        role=user_db.role,
        is_active=user_db.is_active,
        created_at=user_db.created_at
    )
