from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL")

if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

router = APIRouter()

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

# Função para alimentar a lista de formas de pagamento
async def alimentar_lista_formas_pagamento(lista, url, session):
    # Configura a requisição para buscar as formas de pagamento
    headers = {
        "Cookie": f"B1SESSION={session}; ROUTEID=your_route_id"  # Ajuste o ROUTEID conforme necessário
    }
    response = requests.get(url, headers=headers)
    retorno = response.json()

    if retorno.get("error"):
        return retorno

    # Adiciona o retorno à lista
    lista.extend(retorno.get("value", []))

    # Verifica se há mais páginas para buscar
    if retorno.get("odata.nextLink"):
        return await alimentar_lista_formas_pagamento(lista, f"{base_url}/{retorno['odata.nextLink']}", session)

    return lista

@router.get("/")
async def listar_formas_pagamento():
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

    # Chama a função para alimentar a lista de formas de pagamento
    lista_formas_pagamento = await alimentar_lista_formas_pagamento([], f"{base_url}/WizardPaymentMethods?$select=PaymentMethodCode,Description&$filter=Type eq 'boptIncoming'", session)

    return {"formas_pagamento": lista_formas_pagamento}
