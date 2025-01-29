from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL")

if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

router = APIRouter()

class ParansRequestList(BaseModel):
    loja: str

# Função para autenticar o usuário e obter a sessão
async def authenticate_user() -> requests.Response:
    payload = {
        "UserName": os.getenv("USUARIO_LOGIN"),
        "Password": os.getenv("USUARIO_PASSWORD"),
        "CompanyDB": "ECOSISTEMA_FAST",
    }

    headers = {"Content-Type": "application/json"}
    url = f"{base_url}/Login"
    response = requests.post(url, json=payload, headers=headers)

    return response

# Função para buscar todos os vendedores com paginação
async def alimentar_lista(lista, url, session):
    headers = {
        "Cookie": f"B1SESSION={session}; ROUTEID=your_route_id"
    }

    response = requests.get(url, headers=headers)
    retorno = response.json()

    if retorno.get("error"):
        return retorno

    lista.extend(retorno.get("value", []))

    if retorno.get("odata.nextLink"):
        return await alimentar_lista(lista, f"{base_url}/{retorno['odata.nextLink']}", session)

    return lista

@router.post("/")
async def listar_vendedor(parans_request: ParansRequestList):
    # Autentica o usuário e obtém a sessão
    auth_session = await authenticate_user()

    if auth_session.status_code != 200:
        raise HTTPException(
            status_code=auth_session.status_code,
            detail="Falha na autenticação com o serviço externo."
        )

    data = auth_session.json()
    session = data.get("SessionId")

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou não encontrada na resposta do serviço externo."
        )

    # Monta a URL da requisição
    url = f"{base_url}/SalesPersons?$select=SalesEmployeeCode,SalesEmployeeName&$filter=Active eq 'tYES'"

    if parans_request.loja:
        url += f" and U_LOJA eq '{parans_request.loja}'"

    lista_vendedores = await alimentar_lista([], url, session)

    return {"vendedor": lista_vendedores}
