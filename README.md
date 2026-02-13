# fraud-detection-system
Sistema de Detecção de Anomalias em Transações Financeiras
# 🚨 Sistema de Detecção de Anomalias em Transações Financeiras

> Pipeline de dados em tempo real para identificar padrões suspeitos em transações financeiras, inspirado nos sistemas de supervisão de mercado da B3.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Sobre o Projeto

Este projeto simula um sistema de detecção de anomalias em tempo real para transações financeiras, implementando técnicas de engenharia de dados e machine learning para identificar comportamentos suspeitos.

**Principais características:**
- ✅ Processamento de dados em streaming (simulado)
- ✅ Múltiplos algoritmos de detecção de anomalias
- ✅ Pipeline automatizado com Airflow/GitHub Actions
- ✅ Dashboard interativo em tempo real
- ✅ Sistema de alertas configurável
- ✅ Testes de qualidade de dados
- ✅ Documentação completa

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE INGESTÃO                         │
├─────────────────────────────────────────────────────────────────┤
│  Gerador de Transações → Simulação de stream de dados           │
│  (Python + Faker)        (5-10 transações/segundo)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA DE PROCESSAMENTO                       │
├─────────────────────────────────────────────────────────────────┤
│  Validação & Limpeza  →  Feature Engineering  →  Detecção       │
│  - Dados inválidos        - Agregações            - Isolation   │
│  - Duplicatas             - Estatísticas          - Z-Score     │
│  - Formatação             - Padrões temporais     - LOF         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA DE ARMAZENAMENTO                       │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL                                                     │
│  ├── raw_transactions (dados brutos)                            │
│  ├── processed_transactions (dados processados)                 │
│  ├── anomalies (anomalias detectadas)                           │
│  └── alerts (alertas gerados)                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE VISUALIZAÇÃO                       │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard Streamlit                                            │
│  ├── Métricas em tempo real                                     │
│  ├── Gráficos de tendências                                     │
│  ├── Lista de anomalias                                         │
│  └── Análise de padrões                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Stack Tecnológica

### Core
- **Python 3.9+** - Linguagem principal
- **PostgreSQL** - Banco de dados (Supabase free tier)
- **Pandas** - Processamento de dados
- **Scikit-learn** - Algoritmos de ML

### Pipeline & Orquestração
- **GitHub Actions** - CI/CD e agendamento
- **Great Expectations** - Qualidade de dados

### Visualização
- **Streamlit** - Dashboard interativo
- **Plotly** - Gráficos interativos

### Desenvolvimento
- **pytest** - Testes unitários
- **Black** - Formatação de código
- **Flake8** - Linting

## 📂 Estrutura do Projeto

```
fraud-detection-system/
├── .github/
│   └── workflows/
│       ├── pipeline.yml          # GitHub Actions para pipeline
│       └── tests.yml             # Testes automatizados
│
├── src/
│   ├── data_generator/
│   │   ├── __init__.py
│   │   ├── transaction_generator.py  # Gera transações simuladas
│   │   └── config.py                 # Configurações do gerador
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── data_validator.py     # Validação de dados
│   │   └── data_loader.py        # Carrega dados no banco
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── feature_engineering.py    # Criação de features
│   │   ├── anomaly_detection.py      # Algoritmos de detecção
│   │   └── alert_generator.py        # Geração de alertas
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py         # Conexão com PostgreSQL
│   │   └── models.py             # Definição de tabelas
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Sistema de logs
│       └── metrics.py            # Métricas de performance
│
├── streamlit_app/
│   ├── app.py                    # Dashboard principal
│   ├── pages/
│   │   ├── 1_Real_Time.py       # Monitoramento em tempo real
│   │   ├── 2_Analytics.py       # Análises e tendências
│   │   └── 3_Alerts.py          # Gerenciamento de alertas
│   └── utils/
│       └── charts.py             # Funções de visualização
│
├── sql/
│   ├── create_tables.sql         # DDL das tabelas
│   ├── views.sql                 # Views analíticas
│   └── queries.sql               # Queries úteis
│
├── tests/
│   ├── test_generator.py
│   ├── test_validation.py
│   ├── test_detection.py
│   └── test_database.py
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_algorithm_comparison.ipynb
│   └── 03_performance_tuning.ipynb
│
├── config/
│   ├── database.yaml
│   ├── detection_rules.yaml
│   └── alert_thresholds.yaml
│
├── docs/
│   ├── architecture.md
│   ├── algorithms.md
│   ├── deployment.md
│   └── api_documentation.md
│
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Como Começar

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/fraud-detection-system.git
cd fraud-detection-system
```

### 2. Configure o Ambiente
```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configure o Banco de Dados

**Opção A: Supabase (Recomendado - Grátis)**
1. Crie conta em [supabase.com](https://supabase.com)
2. Crie um novo projeto
3. Copie as credenciais e adicione no `.env`

**Opção B: PostgreSQL Local**
```bash
# Instale PostgreSQL
# Execute os scripts SQL
psql -U postgres -f sql/create_tables.sql
```

### 4. Configure Variáveis de Ambiente
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 5. Execute o Pipeline
```bash
# Gera transações e processa
python -m src.main

# Ou rode componentes separadamente
python -m src.data_generator.transaction_generator
python -m src.processing.anomaly_detection
```

### 6. Inicie o Dashboard
```bash
streamlit run streamlit_app/app.py
```

## 📊 Algoritmos de Detecção

### 1. Isolation Forest
- **O que detecta:** Anomalias multivariadas
- **Ideal para:** Padrões complexos que não seguem regras simples
- **Parâmetros:** contamination=0.01 (1% de anomalias esperadas)

### 2. Z-Score (Statistical)
- **O que detecta:** Valores estatisticamente improváveis
- **Ideal para:** Transações com valores muito altos/baixos
- **Parâmetros:** threshold=3 (3 desvios padrão)

### 3. Local Outlier Factor (LOF)
- **O que detecta:** Pontos que diferem significativamente de seus vizinhos
- **Ideal para:** Padrões localmente anômalos
- **Parâmetros:** n_neighbors=20

### 4. Regras de Negócio
- Múltiplas transações em curto período
- Transações acima de limite por categoria
- Transações em horários suspeitos
- Padrões geográficos incomuns

## 🎯 Features Implementadas

### Dados das Transações
- ✅ ID único da transação
- ✅ Timestamp
- ✅ Valor da transação
- ✅ Tipo de transação (PIX, TED, boleto, etc)
- ✅ Categoria (investimento, consumo, transferência)
- ✅ Localização (cidade, estado)
- ✅ Dispositivo utilizado
- ✅ Conta origem e destino

### Features Derivadas
- ✅ Frequência de transações por usuário
- ✅ Valor médio das últimas N transações
- ✅ Desvio do padrão histórico
- ✅ Horário da transação (dia/noite, dia da semana)
- ✅ Velocidade de transações (intervalo entre transações)
- ✅ Distância geográfica da última transação

## 📈 Métricas de Performance

### Qualidade de Detecção
- **Precision:** % de alertas que são realmente anomalias
- **Recall:** % de anomalias detectadas do total
- **F1-Score:** Média harmônica entre precision e recall
- **False Positive Rate:** Taxa de falsos positivos

### Performance do Sistema
- **Throughput:** Transações processadas por segundo
- **Latência:** Tempo médio de processamento
- **Uptime:** Disponibilidade do sistema
- **Data Quality Score:** Pontuação de qualidade dos dados

## 🔄 Pipeline Automatizado

### GitHub Actions (Execução a cada 6 horas)
```yaml
1. Gera batch de transações simuladas
2. Valida qualidade dos dados
3. Processa e detecta anomalias
4. Atualiza métricas no banco
5. Envia alertas se necessário
6. Gera relatório de execução
```

### Monitoramento
- Logs estruturados em JSON
- Métricas exportadas para dashboard
- Alertas por email (configurável)

## 🧪 Testes

```bash
# Execute todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_detection.py -v
```

## 📚 Documentação Adicional

- [Arquitetura Detalhada](docs/architecture.md)
- [Algoritmos de Detecção](docs/algorithms.md)
- [Guia de Deploy](docs/deployment.md)
- [API Documentation](docs/api_documentation.md)

## 🎓 Aprendizados e Desafios

### Técnicas Implementadas
- Streaming de dados simulado
- Feature engineering para séries temporais
- Ensemble de algoritmos de ML
- Data quality com Great Expectations
- CI/CD com GitHub Actions

### Desafios Superados
- Balanceamento entre precision e recall
- Otimização de queries para tempo real
- Gerenciamento de falsos positivos
- Escalabilidade do pipeline

## 🚀 Próximos Passos

- [ ] Implementar Kafka para streaming real
- [ ] Adicionar modelo de ML treinado (XGBoost)
- [ ] Implementar alertas via Telegram/Slack
- [ ] Criar API REST com FastAPI
- [ ] Deploy em cloud (AWS/GCP)
- [ ] Adicionar autenticação no dashboard
- [ ] Implementar feature store

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autores

Mariana Andrade Peres
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- Email: seu.email@exemplo.com
- 
Rafael Oliveira
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- Email: seu.email@exemplo.com

---

⭐ Se este projeto foi útil, considere dar uma estrela!#