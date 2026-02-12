"""
Gerador de transações financeiras simuladas.
Cria dados realistas para testar o sistema de detecção de anomalias.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from faker import Faker

fake = Faker('pt_BR')


class TransactionGenerator:
    """Gera transações financeiras simuladas com padrões realistas e anomalias."""
    
    def __init__(self, anomaly_rate: float = 0.05):
        """
        Args:
            anomaly_rate: Percentual de transações anômalas (default: 5%)
        """
        self.anomaly_rate = anomaly_rate
        self.fake = Faker('pt_BR')
        
        # Configurações de comportamento normal
        self.normal_config = {
            'value_range': (10, 5000),
            'peak_hours': (9, 18),  # Horário comercial
            'types': ['PIX', 'TED', 'Boleto', 'Cartão Débito', 'Cartão Crédito'],
            'categories': ['Alimentação', 'Transporte', 'Saúde', 'Educação', 
                          'Lazer', 'Investimento', 'Transferência'],
        }
        
        # Configurações de anomalias
        self.anomaly_patterns = [
            self._high_value_anomaly,
            self._rapid_transactions,
            self._unusual_time,
            self._unusual_location,
            self._unusual_type_combo,
        ]
    
    def generate_batch(self, n_transactions: int = 1000) -> pd.DataFrame:
        """
        Gera um batch de transações.
        
        Args:
            n_transactions: Número de transações a gerar
            
        Returns:
            DataFrame com as transações
        """
        transactions = []
        n_anomalies = int(n_transactions * self.anomaly_rate)
        n_normal = n_transactions - n_anomalies
        
        # Gera transações normais
        for _ in range(n_normal):
            transactions.append(self._generate_normal_transaction())
        
        # Gera anomalias
        for _ in range(n_anomalies):
            anomaly_func = random.choice(self.anomaly_patterns)
            transactions.append(anomaly_func())
        
        # Shuffle para misturar normais e anômalas
        random.shuffle(transactions)
        
        # Adiciona timestamps sequenciais
        base_time = datetime.now() - timedelta(hours=24)
        for i, trans in enumerate(transactions):
            trans['timestamp'] = base_time + timedelta(
                seconds=random.randint(0, 86400)  # Distribui ao longo de 24h
            )
        
        df = pd.DataFrame(transactions)
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def _generate_normal_transaction(self) -> Dict:
        """Gera uma transação com comportamento normal."""
        trans_type = random.choice(self.normal_config['types'])
        category = random.choice(self.normal_config['categories'])
        
        # Valor varia por categoria
        value_ranges = {
            'Alimentação': (20, 200),
            'Transporte': (10, 100),
            'Saúde': (50, 500),
            'Educação': (100, 1000),
            'Lazer': (30, 300),
            'Investimento': (100, 5000),
            'Transferência': (50, 2000),
        }
        
        min_val, max_val = value_ranges.get(category, (10, 1000))
        value = round(random.uniform(min_val, max_val), 2)
        
        return {
            'transaction_id': str(uuid.uuid4()),
            'user_id': f'USER_{random.randint(1000, 9999)}',
            'value': value,
            'type': trans_type,
            'category': category,
            'merchant': self.fake.company(),
            'city': self.fake.city(),
            'state': self.fake.estado_sigla(),
            'device': random.choice(['Mobile', 'Desktop', 'Tablet']),
            'is_anomaly': False,
            'anomaly_type': None,
        }
    
    def _high_value_anomaly(self) -> Dict:
        """Transação com valor anormalmente alto."""
        trans = self._generate_normal_transaction()
        trans['value'] = round(random.uniform(10000, 50000), 2)
        trans['is_anomaly'] = True
        trans['anomaly_type'] = 'high_value'
        return trans
    
    def _rapid_transactions(self) -> Dict:
        """Transação em sequência rápida (será detectado no processamento)."""
        trans = self._generate_normal_transaction()
        trans['is_anomaly'] = True
        trans['anomaly_type'] = 'rapid_sequence'
        # Marca com flag para processamento posterior detectar sequência
        trans['user_id'] = f'RAPID_{random.randint(1000, 9999)}'
        return trans
    
    def _unusual_time(self) -> Dict:
        """Transação em horário incomum (madrugada)."""
        trans = self._generate_normal_transaction()
        trans['is_anomaly'] = True
        trans['anomaly_type'] = 'unusual_time'
        # Força horário entre 00h-05h (será ajustado no timestamp)
        return trans
    
    def _unusual_location(self) -> Dict:
        """Transação em localização distante das anteriores."""
        trans = self._generate_normal_transaction()
        trans['is_anomaly'] = True
        trans['anomaly_type'] = 'unusual_location'
        # Usa cidade/estado diferente
        trans['city'] = random.choice(['Tóquio', 'Nova York', 'Londres', 'Dubai'])
        trans['state'] = 'EXT'  # Exterior
        return trans
    
    def _unusual_type_combo(self) -> Dict:
        """Combinação incomum de tipo e categoria."""
        trans = self._generate_normal_transaction()
        trans['is_anomaly'] = True
        trans['anomaly_type'] = 'unusual_combo'
        # Combinações estranhas
        weird_combos = [
            ('Boleto', 'Lazer', 10000),
            ('PIX', 'Investimento', 50000),
            ('TED', 'Alimentação', 5000),
        ]
        combo = random.choice(weird_combos)
        trans['type'] = combo[0]
        trans['category'] = combo[1]
        trans['value'] = combo[2]
        return trans
    
    def generate_stream(self, duration_seconds: int = 60, 
                       rate: int = 10) -> List[Dict]:
        """
        Simula stream de transações ao longo do tempo.
        
        Args:
            duration_seconds: Duração do stream em segundos
            rate: Transações por segundo
            
        Returns:
            Lista de transações com timestamps incrementais
        """
        total_transactions = duration_seconds * rate
        return self.generate_batch(total_transactions).to_dict('records')


if __name__ == '__main__':
    # Teste do gerador
    generator = TransactionGenerator(anomaly_rate=0.1)
    
    # Gera batch de teste
    print("Gerando 1000 transações...")
    df = generator.generate_batch(1000)
    
    print(f"\nTotal de transações: {len(df)}")
    print(f"Anomalias detectadas: {df['is_anomaly'].sum()}")
    print(f"Taxa de anomalias: {df['is_anomaly'].mean():.2%}")
    
    print("\nDistribuição por tipo de anomalia:")
    print(df[df['is_anomaly']]['anomaly_type'].value_counts())
    
    print("\nPrimeiras 5 transações:")
    print(df[['transaction_id', 'value', 'type', 'category', 'is_anomaly']].head())
    
    print("\nEstatísticas de valores:")
    print(df['value'].describe())