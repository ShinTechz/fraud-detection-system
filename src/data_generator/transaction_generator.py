import random
import uuid
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from faker import Faker

# Ajuste do path para reconhecer a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.connection import get_db_connection

class TransactionGenerator:
    """Gera transações simuladas com padrões reais e salva no Supabase."""
    
    def __init__(self, anomaly_rate: float = 0.05):
        self.anomaly_rate = anomaly_rate
        self.fake = Faker('pt_BR')
        
        self.normal_config = {
            'types': ['PIX', 'TED', 'Boleto', 'Cartão Débito', 'Cartão Crédito'],
            'categories': ['Alimentação', 'Transporte', 'Saúde', 'Educação', 'Lazer', 'Investimento', 'Transferência'],
        }
        
        self.anomaly_patterns = [
            self._high_value_anomaly,
            self._rapid_transactions,
            self._unusual_time,
            self._unusual_location,
            self._unusual_type_combo,
        ]

    def _generate_normal_transaction(self) -> Dict:
        category = random.choice(self.normal_config['categories'])
        value_ranges = {
            'Alimentação': (20, 200), 'Transporte': (10, 100), 'Saúde': (50, 500),
            'Educação': (100, 1000), 'Lazer': (30, 300), 'Investimento': (100, 5000),
            'Transferência': (50, 2000),
        }
        min_val, max_val = value_ranges.get(category, (10, 1000))
        
        return {
            'transaction_id': str(uuid.uuid4()),
            'user_id': f'USER_{random.randint(1000, 9999)}',
            'value': round(random.uniform(min_val, max_val), 2),
            'type': random.choice(self.normal_config['types']),
            'category': category,
            'merchant': self.fake.company(),
            'city': self.fake.city(),
            'state': self.fake.estado_sigla(),
            'device': random.choice(['Mobile', 'Desktop', 'Tablet']),
            'is_anomaly': False,
            'anomaly_type': 'normal',
        }

    def _high_value_anomaly(self) -> Dict:
        trans = self._generate_normal_transaction()
        trans.update({'value': round(random.uniform(10000, 50000), 2), 'is_anomaly': True, 'anomaly_type': 'high_value'})
        return trans

    def _rapid_transactions(self) -> Dict:
        trans = self._generate_normal_transaction()
        trans.update({'is_anomaly': True, 'anomaly_type': 'rapid_sequence', 'user_id': f'RAPID_{random.randint(1000, 9999)}'})
        return trans

    def _unusual_time(self) -> Dict:
        trans = self._generate_normal_transaction()
        trans.update({'is_anomaly': True, 'anomaly_type': 'unusual_time'})
        return trans

    def _unusual_location(self) -> Dict:
        trans = self._generate_normal_transaction()
        trans.update({'city': random.choice(['Tóquio', 'Londres', 'Dubai']), 'state': 'EX', 'is_anomaly': True, 'anomaly_type': 'unusual_location'})
        return trans

    def _unusual_type_combo(self) -> Dict:
        trans = self._generate_normal_transaction()
        trans.update({'type': 'Boleto', 'category': 'Lazer', 'value': 15000.00, 'is_anomaly': True, 'anomaly_type': 'unusual_combo'})
        return trans

    def generate_batch(self, n_transactions: int = 100) -> pd.DataFrame:
        transactions = []
        n_anomalies = int(n_transactions * self.anomaly_rate)
        for _ in range(n_transactions - n_anomalies): transactions.append(self._generate_normal_transaction())
        for _ in range(n_anomalies): transactions.append(random.choice(self.anomaly_patterns)())
        
        random.shuffle(transactions)
        base_time = datetime.now() - timedelta(hours=24)
        for trans in transactions:
            trans['timestamp'] = base_time + timedelta(seconds=random.randint(0, 86400))
        
        return pd.DataFrame(transactions).sort_values('timestamp').reset_index(drop=True)

    def save_to_db(self, df: pd.DataFrame):
        """Persiste os dados nas tabelas raw e processed do Supabase."""
        engine, session = get_db_connection()
        if not engine: return

        try:
            # 1. Tabela RAW (Dados brutos como chegam da "maquininha")
            df_raw = df.drop(columns=['is_anomaly', 'anomaly_type'])
            df_raw.to_sql('raw_transactions', engine, if_exists='append', index=False)
            
            # 2. Tabela PROCESSED (O que o Dashboard consome)
            df_processed = pd.DataFrame({
                'transaction_id': df['transaction_id'],
                'user_id': df['user_id'],
                'timestamp': df['timestamp'],
                'value': df['value'],
                'is_detected_anomaly': df['is_anomaly'],
                'detected_anomaly_type': df['anomaly_type'],
                'anomaly_score': df['is_anomaly'].apply(lambda x: random.randint(3, 4) if x else 0)
            })
            df_processed.to_sql('processed_transactions', engine, if_exists='append', index=False)
            print(f"✅ {len(df)} transações enviadas ao Supabase!")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
        finally:
            session.close()

if __name__ == '__main__':
    gen = TransactionGenerator(anomaly_rate=0.15) # 15% para o gráfico ficar bonito
    df_batch = gen.generate_batch(150)
    gen.save_to_db(df_batch)