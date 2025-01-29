from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY =  os.getenv("CHAVE_SECRETA")  # Substitua por uma chave segura
ALGORITHM = "HS256"

router = APIRouter()


class TokenValidationRequest(BaseModel):
    token: str


@router.post("/validate")
async def validate_token(request: TokenValidationRequest):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return {"status": "success", "message": "Token válido", "user": username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
