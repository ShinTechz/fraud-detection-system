"""
Dashboard Streamlit para monitoramento de anomalias em tempo real.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configuração da página
st.set_page_config(
    page_title="Sistema de Detecção de Anomalias",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# FUNÇÕES AUXILIARES (simuladas - conectar ao banco depois)
# =====================================================

@st.cache_data(ttl=60)  # Cache por 60 segundos
def load_recent_transactions(hours=24):
    """Carrega transações recentes (MOCK - substituir por query real)."""
    # TODO: Conectar ao PostgreSQL e fazer query real
    # Exemplo de dados mockados
    import numpy as np
    from datetime import datetime, timedelta
    
    n = 1000
    now = datetime.now()
    
    data = {
        'timestamp': [now - timedelta(hours=np.random.randint(0, hours)) for _ in range(n)],
        'transaction_id': [f'TX_{i:06d}' for i in range(n)],
        'user_id': [f'USER_{np.random.randint(1000, 9999)}' for _ in range(n)],
        'value': np.random.lognormal(5, 2, n),
        'is_detected_anomaly': np.random.random(n) < 0.05,
        'anomaly_score': np.random.randint(0, 5, n),
        'detected_anomaly_type': np.random.choice(
            ['normal', 'high_value', 'rapid_sequence', 'unusual_time', 'statistical_outlier'],
            n
        ),
    }
    
    df = pd.DataFrame(data)
    df.loc[~df['is_detected_anomaly'], 'detected_anomaly_type'] = 'normal'
    return df

@st.cache_data(ttl=300)
def load_system_metrics():
    """Carrega métricas do sistema."""
    # TODO: Conectar ao banco
    return {
        'total_transactions': 125430,
        'anomalies_detected': 6271,
        'anomaly_rate': 0.05,
        'avg_processing_time_ms': 45.3,
        'precision': 0.87,
        'recall': 0.82,
        'f1_score': 0.84,
    }

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Configurações")

# Período de análise
time_range = st.sidebar.selectbox(
    "Período de análise",
    ["Última 1 hora", "Últimas 6 horas", "Últimas 24 horas", "Últimos 7 dias"]
)

hours_map = {
    "Última 1 hora": 1,
    "Últimas 6 horas": 6,
    "Últimas 24 horas": 24,
    "Últimos 7 dias": 168
}
hours = hours_map[time_range]

# Filtros
st.sidebar.subheader("Filtros")

severity_filter = st.sidebar.multiselect(
    "Severidade",
    ["LOW", "MEDIUM", "HIGH"],
    default=["MEDIUM", "HIGH"]
)

anomaly_type_filter = st.sidebar.multiselect(
    "Tipo de Anomalia",
    ["high_value", "rapid_sequence", "unusual_time", "unusual_location", "statistical_outlier"],
    default=["high_value", "rapid_sequence"]
)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Sobre este sistema**\n\n"
    "Sistema de detecção de anomalias em transações financeiras "
    "usando ensemble de algoritmos de ML.\n\n"
    "📊 Algoritmos:\n"
    "- Isolation Forest\n"
    "- Z-Score\n"
    "- Local Outlier Factor\n"
    "- Regras de Negócio"
)

# =====================================================
# HEADER
# =====================================================

st.title("🚨 Sistema de Detecção de Anomalias")
st.markdown("### Monitoramento em Tempo Real de Transações Financeiras")

# Auto-refresh
if auto_refresh:
    st.caption(f"🔄 Atualizando a cada 60 segundos... (Última atualização: {datetime.now().strftime('%H:%M:%S')})")

# =====================================================
# MÉTRICAS PRINCIPAIS (KPIs)
# =====================================================

st.markdown("---")

# Carrega dados
df = load_recent_transactions(hours)
metrics = load_system_metrics()

# KPIs em colunas
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📊 Total de Transações",
        value=f"{len(df):,}",
        delta=f"+{int(len(df)*0.05)} vs. período anterior"
    )

with col2:
    anomalies_count = df['is_detected_anomaly'].sum()
    st.metric(
        label="🚨 Anomalias Detectadas",
        value=f"{anomalies_count:,}",
        delta=f"{(anomalies_count/len(df)*100):.2f}%"
    )

with col3:
    st.metric(
        label="⚡ Tempo Médio Proc.",
        value=f"{metrics['avg_processing_time_ms']:.1f}ms",
        delta="-5.2ms",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="🎯 Precision",
        value=f"{metrics['precision']:.2%}",
        delta=f"+{0.03:.2%}"
    )

with col5:
    st.metric(
        label="🔍 Recall",
        value=f"{metrics['recall']:.2%}",
        delta=f"+{0.01:.2%}"
    )

# =====================================================
# GRÁFICOS PRINCIPAIS
# =====================================================

st.markdown("---")
st.subheader("📈 Visualizações")

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Análise Temporal", "Distribuições"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de anomalias ao longo do tempo
        df_hourly = df.set_index('timestamp').resample('1H').agg({
            'transaction_id': 'count',
            'is_detected_anomaly': 'sum'
        }).reset_index()
        df_hourly.columns = ['timestamp', 'total', 'anomalias']
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_hourly['timestamp'],
            y=df_hourly['total'],
            name='Total',
            mode='lines+markers',
            line=dict(color='blue', width=2)
        ))
        fig1.add_trace(go.Scatter(
            x=df_hourly['timestamp'],
            y=df_hourly['anomalias'],
            name='Anomalias',
            mode='lines+markers',
            line=dict(color='red', width=2),
            fill='tozeroy'
        ))
        fig1.update_layout(
            title="Transações e Anomalias por Hora",
            xaxis_title="Horário",
            yaxis_title="Quantidade",
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Distribuição por tipo de anomalia
        anomaly_dist = df[df['is_detected_anomaly']]['detected_anomaly_type'].value_counts()
        
        fig2 = px.pie(
            values=anomaly_dist.values,
            names=anomaly_dist.index,
            title="Distribuição por Tipo de Anomalia",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    # Heatmap de anomalias por hora do dia e dia da semana
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.day_name()
    
    heatmap_data = df[df['is_detected_anomaly']].groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    fig3 = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hora do Dia", y="Dia da Semana", color="Anomalias"),
        title="Heatmap de Anomalias: Dia da Semana vs Hora",
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de valores
        fig4 = px.histogram(
            df,
            x='value',
            color='is_detected_anomaly',
            title="Distribuição de Valores das Transações",
            labels={'value': 'Valor (R$)', 'is_detected_anomaly': 'Anomalia'},
            nbins=50,
            color_discrete_map={True: 'red', False: 'blue'}
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        # Box plot de valores por tipo de anomalia
        anomalies_df = df[df['is_detected_anomaly']]
        
        fig5 = px.box(
            anomalies_df,
            x='detected_anomaly_type',
            y='value',
            title="Valores por Tipo de Anomalia",
            labels={'value': 'Valor (R$)', 'detected_anomaly_type': 'Tipo'}
        )
        st.plotly_chart(fig5, use_container_width=True)

# =====================================================
# TABELA DE ANOMALIAS RECENTES
# =====================================================

st.markdown("---")
st.subheader("🚨 Anomalias Recentes")

# Filtrar apenas anomalias
anomalies_df = df[df['is_detected_anomaly']].copy()
anomalies_df = anomalies_df.sort_values('timestamp', ascending=False)

# Adicionar coluna de severidade (mock)
anomalies_df['severity'] = anomalies_df['anomaly_score'].apply(
    lambda x: 'HIGH' if x >= 3 else 'MEDIUM' if x >= 2 else 'LOW'
)

# Formatar valores
anomalies_df['value_formatted'] = anomalies_df['value'].apply(lambda x: f"R$ {x:,.2f}")
anomalies_df['timestamp_formatted'] = pd.to_datetime(anomalies_df['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')

# Mostrar tabela
display_columns = [
    'timestamp_formatted', 'transaction_id', 'user_id', 
    'value_formatted', 'detected_anomaly_type', 'anomaly_score', 'severity'
]

st.dataframe(
    anomalies_df[display_columns].head(20),
    column_config={
        'timestamp_formatted': 'Data/Hora',
        'transaction_id': 'ID Transação',
        'user_id': 'Usuário',
        'value_formatted': 'Valor',
        'detected_anomaly_type': 'Tipo',
        'anomaly_score': st.column_config.ProgressColumn(
            'Score',
            format='%d',
            min_value=0,
            max_value=4
        ),
        'severity': st.column_config.TextColumn(
            'Severidade'
        )
    },
    hide_index=True,
    use_container_width=True
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Desenvolvido por:** Seu Nome")
    
with col2:
    st.markdown("**Tecnologias:** Python, Streamlit, PostgreSQL, Scikit-learn")
    
with col3:
    st.markdown("**Última atualização:** " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

# Auto-refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()