import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente de um arquivo .env
load_dotenv()

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-para-assinar-cookies")

# Configurações adicionais
DEBUG = os.getenv("DEBUG", "True") == "True"
