from fastapi import APIRouter, HTTPException
import requests
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("BASE_URL")
if not base_url:
    raise ValueError("A variável BASE_URL não está definida no .env!")

router = APIRouter()

def authenticate_user():
    payload = {
        "UserName": os.getenv("USUARIO_LOGIN"),
        "Password": os.getenv("USUARIO_PASSWORD"),
        "CompanyDB": "ECOSISTEMA_FAST",
    }
    headers = {"Content-Type": "application/json"}
    url = f"{base_url}/Login"
    response = requests.post(url, json=payload, headers=headers)
    return response

def alimentar_lista(lista, url, headers):
    response = requests.get(f"{base_url}/{url}", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dados")
    
    retorno = response.json()
    if "error" in retorno:
        raise HTTPException(status_code=400, detail=retorno["error"])
    
    lista.extend(retorno.get("value", []))
    
    if "odata.nextLink" in retorno:
        return alimentar_lista(lista, retorno["odata.nextLink"], headers)
    
    tipoutilizacao = next((item for item in lista if item["ID"] == 10), None)
    tipoutilizacao2 = next((item for item in lista if item["ID"] == 20), None)
    return [tipoutilizacao, tipoutilizacao2]

@router.get("/")
def listar_tipos_utilizacao():
    auth_session = authenticate_user()
    if auth_session.status_code != 200:
        raise HTTPException(status_code=auth_session.status_code, detail="Falha na autenticação com o serviço externo.")
    
    session_data = auth_session.json()
    session_id = session_data.get("SessionId")
    if not session_id:
        raise HTTPException(status_code=401, detail="Sessão inválida ou não encontrada na resposta do serviço externo.")
    
    headers = {"Cookie": f"B1SESSION={session_id}; ROUTEID=your_route_id"}
    url = "NotaFiscalUsage?$select=ID,Description"
    lista_resultado = alimentar_lista([], url, headers)
    
    return {"tipos_utilizacao": lista_resultado}
