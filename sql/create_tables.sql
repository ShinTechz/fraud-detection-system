-- =====================================================
-- SISTEMA DE DETECÇÃO DE ANOMALIAS - DATABASE SCHEMA (POSTGRESQL)
-- =====================================================

-- 1. TABELA DE TRANSAÇÕES BRUTAS
CREATE TABLE IF NOT EXISTS raw_transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    merchant VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    device VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_user_timestamp ON raw_transactions (user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_timestamp ON raw_transactions (timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_value ON raw_transactions (value);

-- 2. TABELA DE TRANSAÇÕES PROCESSADAS
CREATE TABLE IF NOT EXISTS processed_transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    
    -- Features temporais
    hour INT,
    day_of_week INT,
    is_weekend BOOLEAN,
    is_night BOOLEAN,
    
    -- Features do usuário
    user_transaction_count INT,
    user_avg_value DECIMAL(15, 2),
    user_std_value DECIMAL(15, 2),
    deviation_from_avg DECIMAL(10, 4),
    
    -- Features de velocidade
    time_since_last DECIMAL(10, 2),
    transactions_last_hour INT,
    
    -- Scores de detecção
    if_anomaly BOOLEAN,
    if_score DECIMAL(10, 6),
    z_score_anomaly BOOLEAN,
    value_z_score DECIMAL(10, 4),
    lof_anomaly BOOLEAN,
    lof_score DECIMAL(10, 6),
    business_rule_anomaly BOOLEAN,
    rules_triggered_count INT,
    
    -- Resultado final
    is_detected_anomaly BOOLEAN,
    anomaly_score INT,
    detected_anomaly_type VARCHAR(50),
    
    -- Metadata
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (transaction_id) REFERENCES raw_transactions(transaction_id)
);

CREATE INDEX IF NOT EXISTS idx_proc_anomaly ON processed_transactions (is_detected_anomaly);
CREATE INDEX IF NOT EXISTS idx_proc_user_anomaly ON processed_transactions (user_id, is_detected_anomaly);
CREATE INDEX IF NOT EXISTS idx_proc_user_time ON processed_transactions(user_id, timestamp DESC);

-- 3. TABELA DE ANOMALIAS
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    
    -- Classificação
    anomaly_type VARCHAR(50) NOT NULL,
    anomaly_score INT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH
    
    -- Detalhes
    detection_methods JSONB, -- JSONB é melhor para performance no Postgres
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING',
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES raw_transactions(transaction_id)
);

CREATE INDEX IF NOT EXISTS idx_anom_timestamp ON anomalies (timestamp);
CREATE INDEX IF NOT EXISTS idx_anom_status ON anomalies (status);
CREATE INDEX IF NOT EXISTS idx_anom_severity ON anomalies (severity);
CREATE INDEX IF NOT EXISTS idx_anom_type_severity ON anomalies(anomaly_type, severity);

-- 4. TABELA DE ALERTAS
CREATE TABLE IF NOT EXISTS alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    anomaly_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anomaly_id) REFERENCES anomalies(anomaly_id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status);
CREATE INDEX IF NOT EXISTS idx_alerts_time_status ON alerts(timestamp DESC, status);

-- 5. TABELA DE MÉTRICAS
CREATE TABLE IF NOT EXISTS system_metrics (
    metric_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    total_transactions INT,
    anomalies_detected INT,
    anomaly_rate DECIMAL(5, 4),
    avg_processing_time_ms DECIMAL(10, 2),
    throughput_per_second DECIMAL(10, 2),
    f1_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics (timestamp);

-- =====================================================
-- VIEWS ANALÍTICAS
-- =====================================================

CREATE OR REPLACE VIEW v_recent_anomalies AS
SELECT a.*, rt.type, rt.category, rt.city, rt.state
FROM anomalies a
JOIN raw_transactions rt ON a.transaction_id = rt.transaction_id
WHERE a.timestamp >= NOW() - INTERVAL '24 hours';

CREATE OR REPLACE VIEW v_user_statistics AS
SELECT 
    user_id,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN is_detected_anomaly THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(value), 2) as avg_transaction_value
FROM processed_transactions
GROUP BY user_id;

-- =====================================================
-- FUNÇÕES
-- =====================================================

CREATE OR REPLACE FUNCTION get_anomaly_rate(start_date TIMESTAMP, end_date TIMESTAMP)
RETURNS DECIMAL AS $$
DECLARE
    total_count INT;
    anom_count INT;
BEGIN
    SELECT COUNT(*) INTO total_count FROM processed_transactions WHERE timestamp BETWEEN start_date AND end_date;
    SELECT COUNT(*) INTO anom_count FROM processed_transactions WHERE timestamp BETWEEN start_date AND end_date AND is_detected_anomaly = TRUE;
    RETURN CASE WHEN total_count = 0 THEN 0 ELSE ROUND(anom_count::DECIMAL / total_count, 4) END;
END;
$$ LANGUAGE plpgsql;

-- Índice de busca textual (Ajustado para Portuguese)
CREATE INDEX IF NOT EXISTS idx_anomalies_notes_ts ON anomalies USING gin(to_tsvector('portuguese', COALESCE(notes, '')));

-- Comentários
COMMENT ON TABLE raw_transactions IS 'Dados originais de transações financeiras';