import requests

# Função para simular a chamada ao SAP
def get_user_from_sap(user_id: str):
    sap_url = f"https://sap.example.com/api/users/{user_id}"
    response = requests.get(sap_url)
    if response.status_code != 200:
        return None
    return response.json()
