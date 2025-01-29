from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("BASE_URL")

if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

# Configurações do JWT
SECRET_KEY = os.getenv("CHAVE_SECRETA") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# Modelo para receber os dados no formato JSON
class LoginRequest(BaseModel):
    username: str
    password: str


async def authenticate_user(username: str, password: str) -> requests.Response:
    payload = {
        "UserName": username,
        "Password": password,
        "CompanyDB": "ECOSISTEMA_FAST",
    }

    headers = {
        "Content-Type": "application/json"
    }
    url = f"{base_url}/Login"
    response = requests.post(url, json=payload, headers=headers)

    return response

async def info_user(user_code: str, session: str) -> requests.Response:
    headers = {
        "Cookie": f'B1SESSION={session}; ROUTEID'
    }
    url_usuario = f"{base_url}/Users?$select=U_Desconto,UserCode,U_Aprovador&$filter=UserCode eq '{user_code}'"
    response_usuario = requests.get(url_usuario, headers=headers)
    return response_usuario


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login")
async def login_for_access_token(login_request: LoginRequest):
    user_response = await authenticate_user(login_request.username, login_request.password)
    data = user_response.json()
    print(data)
    if "error" in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Agora aguardamos a execução da função info_user
    user_info_response = await info_user(login_request.username, data.get('SessionId'))
    user_data = user_info_response.json()
    print(user_data)
    # Criação do token JWT
    access_token = create_access_token(data={"sub": login_request.username})
    print(user_data)
    return JSONResponse(
        content={
            "message": "Login bem-sucedido",
            "status": "Sucesso",
            "token": access_token,
            "token_type": "bearer",
            "user_info": user_data,
        }
    )   
