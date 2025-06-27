from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.security import decode_token

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            token = credentials.credentials
            if decode_token(token) is None:
                raise HTTPException(403, detail="Token inválido")
            return decode_token(token)
        raise HTTPException(403, detail="Credenciales requeridas")
