from sap_bff.adapters.repositories.sap_repository import get_user_from_sap

def get_user_details(user_id: str):
    user_data = get_user_from_sap(user_id)
    if not user_data:
        return None
    # Processar os dados aqui (transformar no formato necessário para o frontend)
    return {
        "id": user_data.get("ID"),
        "name": user_data.get("Name"),
        "email": user_data.get("Email")
    }
