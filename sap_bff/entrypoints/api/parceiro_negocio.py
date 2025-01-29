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

router = APIRouter()

# Modelo para receber os dados no formato JSON
class ParansRequestList(BaseModel):
    cpf_cnpj: str
    codigo_parceiro: str
    nome_parceiro: str


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

@router.post("/listar")
async def list_parceiros(parans_request: ParansRequestList):
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
    url_parceiros_negocio = (
        f"{base_url}/BusinessPartners?$filter=contains(CardCode,'{parans_request.codigo_parceiro}') "
        f"and contains(CardName,'{parans_request.nome_parceiro}')"
    )

    try:
        response = requests.get(url_parceiros_negocio, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Erro ao buscar parceiros de negócios no serviço externo."
            )
        
        parceiros_data = response.json()
        return {"parceiros": parceiros_data}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro ao processar a requisição: {str(e)}"
        )