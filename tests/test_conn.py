import sys
import os

# Garante que o Python encontre a pasta 'src' na raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.connection import get_db_connection

def test_connection():
    print("🔍 Iniciando teste de conexão com Supabase...")
    engine, session = get_db_connection()
    
    if engine and session:
        try:
            # Tenta uma consulta simples para validar a comunicação
            from sqlalchemy import text
            result = session.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Conexão estabelecida com sucesso!")
                print("📡 Supabase respondeu: 'SELECT 1' OK.")
        except Exception as e:
            print(f"❌ Conexão física ok, mas erro na consulta: {e}")
        finally:
            session.close()
    else:
        print("❌ Falha crítica: Não foi possível criar o engine de conexão.")

if __name__ == "__main__":
    test_connection()