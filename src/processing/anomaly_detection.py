"""
Sistema de detecção de anomalias usando múltiplos algoritmos.
Implementa Isolation Forest, Z-Score, LOF e regras de negócio.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detector de anomalias usando ensemble de algoritmos."""
    
    def __init__(self, contamination: float = 0.05):
        """
        Args:
            contamination: Proporção esperada de anomalias nos dados
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
        
        # Inicializa modelos
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        self.lof = LocalOutlierFactor(
            contamination=contamination,
            n_neighbors=20,
            novelty=False
        )
        
        # Thresholds para regras
        self.z_score_threshold = 3
        self.business_rules = {
            'max_value_single': 10000,
            'max_transactions_per_hour': 10,
            'suspicious_hours': (0, 5),  # 00h às 05h
            'max_distance_km': 500,  # Distância máxima esperada entre transações
        }
    
    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta anomalias usando ensemble de métodos.
        
        Args:
            df: DataFrame com transações
            
        Returns:
            DataFrame com colunas adicionais de detecção
        """
        logger.info(f"Iniciando detecção em {len(df)} transações...")
        
        # Cria features para detecção
        df_features = self._create_features(df.copy())
        
        # Aplica cada método de detecção
        df_features = self._isolation_forest_detection(df_features)
        df_features = self._z_score_detection(df_features)
        df_features = self._lof_detection(df_features)
        df_features = self._business_rules_detection(df_features)
        
        # Combina resultados (voting)
        df_features['anomaly_score'] = (
            df_features['if_anomaly'].astype(int) +
            df_features['z_score_anomaly'].astype(int) +
            df_features['lof_anomaly'].astype(int) +
            df_features['business_rule_anomaly'].astype(int)
        )
        
        # Considera anomalia se 2+ métodos detectaram
        df_features['is_detected_anomaly'] = df_features['anomaly_score'] >= 2
        
        # Identifica qual tipo de anomalia
        df_features['detected_anomaly_type'] = df_features.apply(
            self._classify_anomaly_type, axis=1
        )
        
        logger.info(f"Detecção concluída. Anomalias encontradas: "
                   f"{df_features['is_detected_anomaly'].sum()}")
        
        return df_features
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features derivadas para detecção."""
        df = df.copy()
        
        # Features temporais
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = df['hour'].between(0, 5).astype(int)
        
        # Features por usuário
        df['user_transaction_count'] = df.groupby('user_id')['transaction_id'].transform('count')
        df['user_avg_value'] = df.groupby('user_id')['value'].transform('mean')
        df['user_std_value'] = df.groupby('user_id')['value'].transform('std').fillna(0)
        df['deviation_from_avg'] = (df['value'] - df['user_avg_value']) / (df['user_std_value'] + 1)
        
        # Features de velocidade de transações
        df_sorted = df.sort_values(['user_id', 'timestamp'])
        df_sorted['time_since_last'] = df_sorted.groupby('user_id')['timestamp'].diff().dt.total_seconds()
        df = df.merge(
            df_sorted[['transaction_id', 'time_since_last']], 
            on='transaction_id', 
            how='left'
        )
        df['time_since_last'] = df['time_since_last'].fillna(3600)  # 1h default
        
        # Encoding de categorias
        df['type_encoded'] = pd.Categorical(df['type']).codes
        df['category_encoded'] = pd.Categorical(df['category']).codes
        df['device_encoded'] = pd.Categorical(df['device']).codes
        
        return df
    
    def _isolation_forest_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalias usando Isolation Forest."""
        # Seleciona features numéricas para o modelo
        feature_cols = [
            'value', 'hour', 'day_of_week', 'user_transaction_count',
            'deviation_from_avg', 'time_since_last', 'type_encoded',
            'category_encoded', 'device_encoded'
        ]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Predição (-1 para anomalia, 1 para normal)
        predictions = self.isolation_forest.fit_predict(X_scaled)
        df['if_anomaly'] = (predictions == -1)
        
        # Score de anomalia (quanto mais negativo, mais anômalo)
        df['if_score'] = self.isolation_forest.score_samples(X_scaled)
        
        return df
    
    def _z_score_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalias usando Z-Score em valores."""
        # Calcula Z-score global para valores
        mean_value = df['value'].mean()
        std_value = df['value'].std()
        df['value_z_score'] = np.abs((df['value'] - mean_value) / std_value)
        
        # Também calcula Z-score por usuário
        df['value_z_score_user'] = df.groupby('user_id')['value'].transform(
            lambda x: np.abs((x - x.mean()) / (x.std() + 0.01))
        )
        
        # Anomalia se Z-score global OU por usuário exceder threshold
        df['z_score_anomaly'] = (
            (df['value_z_score'] > self.z_score_threshold) |
            (df['value_z_score_user'] > self.z_score_threshold)
        )
        
        return df
    
    def _lof_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalias usando Local Outlier Factor."""
        feature_cols = [
            'value', 'hour', 'deviation_from_avg', 'time_since_last'
        ]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # LOF retorna -1 para anomalias
        predictions = self.lof.fit_predict(X_scaled)
        df['lof_anomaly'] = (predictions == -1)
        
        # Negative outlier factor (quanto menor, mais anômalo)
        df['lof_score'] = self.lof.negative_outlier_factor_
        
        return df
    
    def _business_rules_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica regras de negócio para detecção sem quebrar o índice."""
        # 1. Preparação: Converter para datetime e garantir que o índice original seja preservado
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(['user_id', 'timestamp'])
        
        # Guardamos o índice original para reordenar no final
        original_index = df.index
        
        # Regra 1: Valor único muito alto
        rule1 = df['value'] > self.business_rules['max_value_single']
        
        # Regra 2: Horário suspeito (madrugada)
        rule2 = df['hour'].between(*self.business_rules['suspicious_hours'])
        
        # Regra 3: Muitas transações em curto período (AQUI ESTÁ A CORREÇÃO)
        # Usamos transform com rolling para garantir que o tamanho (1000) seja mantido
        df['transactions_last_hour'] = (
            df.set_index('timestamp')
            .groupby('user_id')['transaction_id'] # Selecionamos uma coluna qualquer para contar
            .rolling('1h')
            .count()
            .reset_index(level=0, drop=True) # Remove o user_id do índice duplo do rolling
            .values
        )
        rule3 = df['transactions_last_hour'] > self.business_rules['max_transactions_per_hour']
        
        # Regra 4: Intervalo muito curto entre transações
        rule4 = df['time_since_last'] < 30
        
        # 2. Combinação das Regras
        # Criamos um DataFrame auxiliar para as regras com o mesmo índice do df
        rules_df = pd.DataFrame({
            'r1': rule1,
            'r2': rule2,
            'r3': rule3,
            'r4': rule4
        }, index=df.index)
        
        df['business_rule_anomaly'] = rules_df.any(axis=1)
        df['rules_triggered_count'] = rules_df.sum(axis=1)
        
        # 3. Restaurar a ordem original para não quebrar outros processos
        return df.loc[original_index]
    
    def _classify_anomaly_type(self, row: pd.Series) -> str:
        """Classifica o tipo de anomalia detectada."""
        if not row['is_detected_anomaly']:
            return 'normal'
        
        # Prioriza tipos mais específicos
        if row['value_z_score'] > self.z_score_threshold:
            return 'high_value'
        elif row['is_night']:
            return 'unusual_time'
        elif row['time_since_last'] < 30:
            return 'rapid_sequence'
        elif row['rules_triggered_count'] > 1:
            return 'multiple_rules'
        else:
            return 'statistical_outlier'
    
    def generate_alert(self, anomaly_row: pd.Series) -> Dict:
        """
        Gera alerta estruturado para uma anomalia.
        
        Args:
            anomaly_row: Linha do DataFrame representando a anomalia
            
        Returns:
            Dicionário com informações do alerta
        """
        severity = 'HIGH' if anomaly_row['anomaly_score'] >= 3 else 'MEDIUM'
        
        alert = {
            'alert_id': f"ALERT_{anomaly_row['transaction_id'][:8]}",
            'timestamp': anomaly_row['timestamp'],
            'severity': severity,
            'transaction_id': anomaly_row['transaction_id'],
            'user_id': anomaly_row['user_id'],
            'value': anomaly_row['value'],
            'anomaly_type': anomaly_row['detected_anomaly_type'],
            'anomaly_score': anomaly_row['anomaly_score'],
            'details': {
                'isolation_forest': bool(anomaly_row['if_anomaly']),
                'z_score': bool(anomaly_row['z_score_anomaly']),
                'lof': bool(anomaly_row['lof_anomaly']),
                'business_rules': bool(anomaly_row['business_rule_anomaly']),
                'if_score': float(anomaly_row['if_score']),
                'value_z_score': float(anomaly_row['value_z_score']),
            }
        }
        
        return alert


if __name__ == '__main__':
    # Teste do detector
    from src.data_generator.transaction_generator import TransactionGenerator
    
    print("Gerando transações de teste...")
    generator = TransactionGenerator(anomaly_rate=0.1)
    df = generator.generate_batch(1000)
    
    print("\nDetectando anomalias...")
    detector = AnomalyDetector(contamination=0.1)
    results = detector.detect(df)
    
    print(f"\n=== RESULTADOS ===")
    print(f"Total de transações: {len(results)}")
    print(f"Anomalias reais (ground truth): {df['is_anomaly'].sum()}")
    print(f"Anomalias detectadas: {results['is_detected_anomaly'].sum()}")
    
    # Métricas de performance
    if 'is_anomaly' in df.columns:
        from sklearn.metrics import classification_report, confusion_matrix
        
        print("\n=== MÉTRICAS DE DETECÇÃO ===")
        print(classification_report(
            df['is_anomaly'], 
            results['is_detected_anomaly'],
            target_names=['Normal', 'Anomalia']
        ))
        
        print("\nMatriz de Confusão:")
        print(confusion_matrix(df['is_anomaly'], results['is_detected_anomaly']))
    
    print("\n=== DISTRIBUIÇÃO POR TIPO DE ANOMALIA DETECTADA ===")
    print(results[results['is_detected_anomaly']]['detected_anomaly_type'].value_counts())
    
    print("\n=== EXEMPLOS DE ANOMALIAS DETECTADAS ===")
    anomalies = results[results['is_detected_anomaly']].head()
    print(anomalies[['transaction_id', 'value', 'anomaly_score', 'detected_anomaly_type']])