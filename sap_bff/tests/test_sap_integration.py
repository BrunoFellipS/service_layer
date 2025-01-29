from fastapi.testclient import TestClient
from sap_bff.entrypoints.main import app

client = TestClient(app)

def test_login():
    response = client.post("/login", data={"username": "johndoe", "password": "secret"})
    assert response.status_code == 200
    assert response.cookies["user_id"] == "johndoe"

def test_get_user_from_sap():
    response = client.get("/sap/user/johndoe")
    assert response.status_code == 200
    assert "name" in response.json()
