from fastapi import APIRouter, HTTPException, Depends
from sap_bff.domain.services.sap_service import get_user_details

router = APIRouter()

@router.get("/sap/user/{user_id}")
async def get_user_from_sap(user_id: str):
    user_data = get_user_details(user_id)
    if not user_data:
        raise HTTPException(status_code=500, detail="Erro ao consultar dados no SAP")
    return user_data
