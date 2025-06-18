from dotenv import load_dotenv
import os

# Carrega automaticamente as variáveis do arquivo .env
load_dotenv()

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
URL_SISTEMA = os.getenv("URL_SISTEMA")
