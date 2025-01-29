from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sap_bff.entrypoints.api import (
    auth_router, sap_router, authtoken, orcamento, parceiro_negocio,
    loja, filial, deposito, vendedor, forma_pagamento, condicao_pagamento,
    lista_preco, utilizacao
)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Endereço do frontend
        "http://127.0.0.1:3000",  # Alternativa para localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de roteadores com seus respectivos prefixos e tags
routers = [
    (auth_router, "/auth", "auth"),
    (sap_router, "/sap", "sap"),
    (authtoken, "/token", "token"),
    (orcamento, "/orcamento", "orçamentos"),
    (parceiro_negocio, "/parceiro", "parceiro"),
    (loja, "/loja", "loja"),
    (filial, "/filial", "filial"),
    (deposito, "/deposito", "deposito"),
    (vendedor, "/vendedor", "vendedor"),
    (forma_pagamento, "/forma-pagamento", "forma pagamento"),
    (condicao_pagamento, "/condicao-pagamento", "condição pagamento"),
    (lista_preco, "/lista-preco", "lista preço"),
    (utilizacao, "/utilizacao", "utilização"),
]

# Inclusão dinâmica dos roteadores
for router, prefix, tag in routers:
    app.include_router(router.router, prefix=prefix, tags=[tag])
