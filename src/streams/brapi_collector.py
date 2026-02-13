import requests
import os
import pandas as pd
from dotenv import load_dotenv
from src.database.connection import get_db_connection

load_dotenv()

class BrapiCollector:
    def __init__(self):
        self.token = os.getenv("BRAPI_TOKEN")
        self.base_url = "https://brapi.dev/api/quote/"

    def fetch_prices(self, tickers="PETR4,VALE3,BTC"):
        url = f"{self.base_url}{tickers}?token={self.token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()['results']
        except Exception as e:
            print(f"❌ Erro na Brapi: {e}")
            return []

    def save_to_db(self, data):
        if not data:
            print("⚠️ Nenhum dado para salvar.")
            return

        engine, session = get_db_connection()
        if not engine:
            return

        try:
            # Converte para DataFrame para facilitar o mapeamento
            df = pd.DataFrame(data)

            # Mapeia os campos da API para as colunas do seu SQL
            df_mapped = pd.DataFrame({
                'symbol': df['symbol'],
                'short_name': df.get('shortName'),
                'price': df['regularMarketPrice'],
                'change_percent': df['regularMarketChangePercent'],
                'market_cap': df.get('marketCap'),
                'volume_24h': df.get('regularMarketVolume'),
                'timestamp': pd.to_datetime(df['regularMarketTime'])
            })

            # Salva no banco (append para manter histórico)
            df_mapped.to_sql('market_data', engine, if_exists='append', index=False)
            print(f"✅ {len(df_mapped)} registros salvos na tabela market_data!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar no banco: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    collector = BrapiCollector()
    
    print("📡 Coletando dados da Brapi...")
    precos = collector.fetch_prices()
    
    if precos:
        print("💾 Salvando no Supabase...")
        collector.save_to_db(precos)