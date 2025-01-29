from fastapi import APIRouter, HTTPException, Request
import requests
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL")

if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

router = APIRouter()


class ParansRequestList(BaseModel):
    estado: str

# Função para autenticar o usuário e obter a sessão
async def authenticate_user() -> requests.Response:
    payload = {
        "UserName": os.getenv("USUARIO_LOGIN"),
        "Password": os.getenv("USUARIO_PASSWORD"),
        "CompanyDB": "ECOSISTEMA_FAST",
    }

    headers = {
        "Content-Type": "application/json"
    }
    url = f"{base_url}/Login"
    response = requests.post(url, json=payload, headers=headers)

    return response

# Função para alimentar a lista com paginação
async def alimentar_lista(lista, url, session):
    headers = {
        "Cookie": f"B1SESSION={session}; ROUTEID=your_route_id"  # Ajuste o ROUTEID conforme necessário
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
async def listar_price_lists(parans_request: ParansRequestList ):
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

    url = f"{base_url}/PriceLists?$select=PriceListName,PriceListNo&$filter=not contains(PriceListName, 'CUSTO')"
    if parans_request.estado:
        url = f"{url} and contains(U_ESTADO,'{parans_request.estado}')"

    lista_price_lists = await alimentar_lista([], url, session)

    return {"price_lists": lista_price_lists}
