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

class ParansRequestList(BaseModel):
    loja: str

if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

# Configurações do JWT
router = APIRouter()

async def authenticate_user() -> requests.Response:
    payload = {
        "UserName": os.getenv("USUARIO_LOGIN") ,
        "Password": os.getenv("USUARIO_PASSWORD") ,
        "CompanyDB": "ECOSISTEMA_FAST",
    }

    headers = {
        "Content-Type": "application/json"
    }
    url = f"{base_url}/Login"
    response = requests.post(url, json=payload, headers=headers)

    return response

@router.post("/")
async def listar_filial(parans_request: ParansRequestList):
    # Autentica o usuário e obtém a sessão
    auth_session = await authenticate_user()

    # Verifica se a autenticação foi bem-sucedida
    if auth_session.status_code != 200:
        raise HTTPException(
            status_code=auth_session.status_code,
            detail="Falha na autenticação com o serviço externo."
        )
    
    data = auth_session.json()

    # Extrai a sessão do B1
    session = data.get("SessionId")
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou não encontrada na resposta do serviço externo."
        )

    # Configura a requisição para obter os parceiros de negócios
    headers = {
        "Cookie": f"B1SESSION={session}; ROUTEID=your_route_id"  # Ajuste ROUTEID conforme necessário
    }

    url = f"{base_url}/Warehouses?$select=WarehouseCode,WarehouseName,BusinessPlaceID,U_LOJA"
    
    if parans_request.loja != "":
        url = f"{url}&$filter=U_LOJA eq '{parans_request.loja}'"

    depositos_request = requests.get(url, headers=headers)
    depositos_json = depositos_request.json()
    depositos_json = depositos_json.get("value")

    return {"deposito": depositos_json}