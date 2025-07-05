from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models.userModel import UserCreate, UserLogin, LoginResponse, UserPublic,UserCreateResponse
from service.auth_service import create_user, authenticate_user
from config.security import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserCreateResponse)
def register(user_create: UserCreate):
    user = create_user(user_create)
    return {
        "message": "Usuario creado exitosamente",
        "data": user
    }

@router.post("/login", response_model=LoginResponse)
def login(user_login: UserLogin):
    user = authenticate_user(user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    token = create_access_token(jsonable_encoder(user))  # <- convierte todo a JSON válido
    return {
        "message": "Login exitoso",
        "access_token": token,
        "token_type": "bearer"
    }
