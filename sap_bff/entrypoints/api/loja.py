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

@router.get("/")
async def listar_lojas():
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
    url_lista_loja = f"{base_url}/SQLQueries('Lojas')/List"
    lista_loja = requests.get(url_lista_loja, headers=headers)
    lojas_json = lista_loja.json()
    lojas = lojas_json.get("value")
    if lojas_json.get("odata.nextLink"):
        url = f"{base_url}/{lojas_json.get('odata.nextLink')}"
        lista_loja_next = requests.get(url, headers=headers)
        lojas_next = lista_loja_next.json()
        lojas_next = lojas_next.get("value")
        lojas = lojas + lojas_next
    lojas_excluidas = ['08', '15', '21', '27']  # IDs a serem removidos

    # Filtra os itens cujo 'Code' NÃO está em 'lojas'
    lista_filtrada = [item for item in lojas if item['Code'] not in lojas_excluidas]

    return {"lojas":lista_filtrada}