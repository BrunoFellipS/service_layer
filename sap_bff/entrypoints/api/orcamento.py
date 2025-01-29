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


# Modelo para receber os dados no formato JSON
class ParansRequestList(BaseModel):
    codigo: str
    codigo_parceiro: str
    nome_parceiro: str
    data_inicio: str
    data_fim: str

class ParansRequestFindOne(BaseModel):
    codigo: str

class ParansRequestVendedor(BaseModel):
    codigo_vendedor: str

async def orcamentoList(codigo: str, codigo_parceiro: str, nome_parceiro:str, data_inicio: str, data_fim: str ,session: str ) -> requests.Response:
    headers = {
        "Cookie": f'B1SESSION={session}; ROUTEID'
    }
    # and contains(DocEntry, '${docEntry}')
    url_usuario = f"{base_url}/Quotations?$select=DocNum,CardCode,CardName,DocDate,DocTotal,DocDueDate"

    filtros = []

    if data_inicio:
        filtros.append(f"DocDate ge '{data_inicio}'")
    if data_fim:
        filtros.append(f"DocDate le '{data_fim}'")
    if codigo:
        filtros.append(f"contains(DocNum, '{codigo}')")
    if codigo_parceiro:
        filtros.append(f"contains(CardCode, '{codigo_parceiro}')")
    if nome_parceiro:
        filtros.append(f"contains(CardName, '{nome_parceiro}')")

    if filtros:
        url_usuario += "&$filter=" + " and ".join(filtros)

    url_usuario += "&$orderby=DocDate desc"
    print(url_usuario)
    response_usuario = requests.get(url_usuario, headers=headers)
    return response_usuario


async def orcamentoById(codigo: str,session: str ) -> requests.Response:
    headers = {
        "Cookie": f'B1SESSION={session}; ROUTEID'
    }
    # and contains(DocEntry, '${docEntry}')
    url_usuario = f"{base_url}/Quotations?$filter=Docnum eq '{codigo}'"
    print(url_usuario)
    response_usuario = requests.get(url_usuario, headers=headers)
    return response_usuario


@router.post("/por-list")
async def buscar_orcamentos(parans_request: ParansRequestList):
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

    # Chamada para buscar orçamentos por vendedor
    orcamento_response = await orcamentoList(
        codigo=parans_request.codigo,
        codigo_parceiro=parans_request.codigo_parceiro,
        nome_parceiro=parans_request.nome_parceiro,
        data_inicio=parans_request.data_inicio,
        data_fim=parans_request.data_fim,
        session=session
    )

    # Verifica se a busca foi bem-sucedida
    if orcamento_response.status_code != 200:
        raise HTTPException(
            status_code=orcamento_response.status_code,
            detail="Erro ao buscar orçamentos."
        )

    # Processa a resposta dos orçamentos
    orcamento_data = orcamento_response.json()

    # Retorna o JSON com os dados processados
    return JSONResponse(
        content={"status": "sucesso", "orcamentos": orcamento_data},
        status_code=200
    )


@router.post("/orcamento-detalhe")
async def orcamento_detalhe(parans_request_findone: ParansRequestFindOne):
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

    # Configura a requisição para obter o detalhe do orçamento
    headers = {
        "Cookie": f"B1SESSION={session}; ROUTEID"
    }
    url_detalhe_orcamento = f"{base_url}/Quotations?$filter=DocNum eq '{parans_request_findone.codigo}'"
    response = requests.get(url_detalhe_orcamento, headers=headers)

    # Verifica se a busca foi bem-sucedida
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Erro ao buscar o detalhe do orçamento."
        )

    # Processa a resposta do orçamento
    orcamento_detalhe = response.json()

    # Retorna o detalhe do orçamento
    return JSONResponse(
        content={"status": "sucesso", "detalhe_orcamento": orcamento_detalhe},
        status_code=200
    )

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


@router.post("/orcamento-")
async def orcamento_detalhe(parans_request: ParansRequestFindOne):
    pass