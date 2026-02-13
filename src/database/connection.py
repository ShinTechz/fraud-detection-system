import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Buscando as variáveis separadas
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")

    # Montando a URL de forma limpa
    # O driver 'postgresql+psycopg2' é o mais estável
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        return engine, Session()
    except Exception as e:
        print(f"❌ Erro ao configurar conexão: {e}")
        return None, None