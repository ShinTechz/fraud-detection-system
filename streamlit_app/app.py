import sys
import os

# 1. PRIMEIRO: Configura o caminho (sobe um nível para achar a pasta raiz)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. SEGUNDO: Importa os outros pacotes e a sua SRC
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Agora o Python sabe onde encontrar isso:
from src.database.connection import get_db_connection

# Configuração da página
st.set_page_config(
    page_title="Sistema de Detecção de Anomalias",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para manter o visual limpo
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# FUNÇÕES DE CARREGAMENTO DE DADOS (SQL REAL)
# =====================================================

@st.cache_data(ttl=60)
def load_market_data():
    """Carrega os preços mais recentes da Brapi salvos no banco."""
    engine, _ = get_db_connection()
    if engine:
        # Pega o registro mais recente para cada símbolo
        query = """
            SELECT DISTINCT ON (symbol) symbol, price, change_percent, timestamp 
            FROM market_data 
            ORDER BY symbol, timestamp DESC
        """
        try:
            return pd.read_sql(query, engine)
        except Exception as e:
            st.error(f"Erro ao carregar mercado: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_transaction_data(hours=24):
    """Carrega transações processadas do banco de dados."""
    engine, _ = get_db_connection()
    if engine:
        query = f"""
            SELECT * FROM processed_transactions 
            WHERE timestamp >= NOW() - INTERVAL '{hours} hours'
            ORDER BY timestamp DESC
        """
        try:
            df = pd.read_sql(query, engine)
            # Se o banco estiver vazio, criamos um DF vazio com as colunas certas
            if df.empty:
                return pd.DataFrame(columns=['timestamp', 'value', 'is_detected_anomaly', 'detected_anomaly_type'])
            return df
        except Exception as e:
            st.error(f"Erro ao carregar transações: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_system_metrics():
    """Busca métricas da tabela de métricas do sistema."""
    engine, _ = get_db_connection()
    if engine:
        query = "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1"
        try:
            df = pd.read_sql(query, engine)
            if not df.empty:
                return df.iloc[0].to_dict()
        except:
            pass
    # Fallback caso a tabela de métricas esteja vazia
    return {
        'total_transactions': 0,
        'anomalies_detected': 0,
        'precision': 0.0,
        'recall': 0.0,
        'avg_processing_time_ms': 0.0
    }

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Configurações")
time_range = st.sidebar.selectbox(
    "Período de análise",
    ["Última 1 hora", "Últimas 6 horas", "Últimas 24 horas", "Últimos 7 dias"]
)

hours_map = {"Última 1 hora": 1, "Últimas 6 horas": 6, "Últimas 24 horas": 24, "Últimos 7 dias": 168}
hours = hours_map[time_range]

auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica de Portfólio**\n\nEste dashboard consome dados via SQLAlchemy do Supabase em tempo real.")

# =====================================================
# HEADER E TICKER DE MERCADO (BRA PI)
# =====================================================

st.title("🚨 Sistema de Detecção de Anomalias")
st.markdown("### Monitoramento em Tempo Real de Transações Financeiras")

# Ticker de Mercado
market_df = load_market_data()
if not market_df.empty:
    market_cols = st.columns(len(market_df))
    for i, row in market_df.iterrows():
        with market_cols[i]:
            st.metric(
                label=f"💰 {row['symbol']}",
                value=f"R$ {row['price']:,.2f}",
                delta=f"{row['change_percent']:.2f}%",
                delta_color="normal" if row['change_percent'] >= 0 else "inverse"
            )

if auto_refresh:
    st.caption(f"🔄 Atualizado em: {datetime.now().strftime('%H:%M:%S')}")

# =====================================================
# MÉTRICAS PRINCIPAIS (KPIs)
# =====================================================

df = load_transaction_data(hours)
metrics = load_system_metrics()

st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Total Analisado", f"{len(df):,}")
with col2:
    anomalies_count = df['is_detected_anomaly'].sum() if not df.empty else 0
    st.metric("🚨 Anomalias", f"{anomalies_count:,}", delta=f"{(anomalies_count/(len(df) if len(df)>0 else 1)*100):.2f}%", delta_color="inverse")
with col3:
    st.metric("⚡ Latência Média", f"{metrics['avg_processing_time_ms']:.1f}ms")
with col4:
    st.metric("🎯 Precision", f"{metrics['precision']:.1%}")
with col5:
    st.metric("🔍 Recall", f"{metrics['recall']:.1%}")

# =====================================================
# GRÁFICOS
# =====================================================

st.markdown("---")
if not df.empty:
    tab1, tab2 = st.tabs(["Visão Temporal", "Distribuição"])
    
    with tab1:
        # Gráfico de Linhas (Total vs Anomalias)
        df_hourly = df.set_index(pd.to_datetime(df['timestamp'])).resample('1H').agg({
            'is_detected_anomaly': ['count', 'sum']
        }).reset_index()
        df_hourly.columns = ['timestamp', 'total', 'anomalias']

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_hourly['timestamp'], y=df_hourly['total'], name='Total', line=dict(color='#3498db')))
        fig.add_trace(go.Scatter(x=df_hourly['timestamp'], y=df_hourly['anomalias'], name='Anomalias', line=dict(color='#e74c3c'), fill='tozeroy'))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Pizza por Tipo de Anomalia
        if anomalies_count > 0:
            fig_pie = px.pie(df[df['is_detected_anomaly']], names='detected_anomaly_type', title="Tipos de Fraude Detectados")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Nenhuma anomalia detectada no período para gerar o gráfico.")
else:
    st.warning("Aguardando novas transações serem inseridas no banco...")

# =====================================================
# TABELA FINAL
# =====================================================

st.subheader("📋 Últimas Transações Processadas")
st.dataframe(df.head(15), use_container_width=True, hide_index=True)

# Controle de Refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()