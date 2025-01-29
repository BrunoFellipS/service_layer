from passlib.context import CryptContext
from sap_bff.domain.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Lista de usuários fictícios
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "password": pwd_context.hash("secret"),
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user
