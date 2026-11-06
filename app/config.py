import os
from pathlib import Path
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env')
class Settings:
    APP_NAME=os.getenv('APP_NAME','Claude2 Predictive CRM')
    DATABASE_URL=os.getenv('DATABASE_URL',f"sqlite:///{ROOT/'data'/'crm.db'}")
    OLLAMA_BASE_URL=os.getenv('OLLAMA_BASE_URL','http://localhost:11434').rstrip('/')
    OLLAMA_MODEL=os.getenv('OLLAMA_MODEL','llama3.2:3b')
    OLLAMA_CONNECT_TIMEOUT=int(os.getenv('OLLAMA_CONNECT_TIMEOUT','5'))
    OLLAMA_TIMEOUT=int(os.getenv('OLLAMA_TIMEOUT','300'))
settings=Settings()
