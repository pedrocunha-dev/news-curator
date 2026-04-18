import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (principalmente OPENAI_API_KEY)
load_dotenv()

# Constantes globais do pipeline
MIN_FONTES = 3
MAX_TENTATIVAS_APURACAO = 3

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")