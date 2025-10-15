import streamlit as st
from datetime import datetime
import pandas as pd

# Importações dos módulos refatorados
from utils.data_loader import load_data
from utils.plotting import format_currency, format_number
from tabs.overview import display_overview
from tabs.inicio import display_inicio
from tabs.maturidade import display_maturidade
from tabs.expansao import display_expansao
from tabs.declinio import display_declinio
from tabs.detalhamento import display_detalhamento
from tabs.comparacao import display_comparacao

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise de Transações",
    page_icon="📊",
    layout="wide"
)

# --- Estilização Customizada (CSS) ---
st.markdown("""
<style>
    /* Cor de fundo da sidebar */
    [data-testid="stSidebar"] {
        background-color: #C30000;
    }
    /* Cor do texto e ícones na sidebar */
    [data-testid="stSidebar"] .st-emotion-cache-17351a4,
    [data-testid="stSidebar"] .st-emotion-cache-q1623p,
    [data-testid="stSidebar"] .st-emotion-cache-1gulkj5,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white;
    }
    /* Estilo dos cards de KPI na sidebar */
    .kpi-card {
        background: linear-gradient(145deg, #C30000, #FF4D4D);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .kpi-title {
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: bolder;
    }
</style>
""", unsafe_allow_html=True)

# --- Carregar os dados ---
df_main, base_id, base_transacoes, calendario = load_data()

if df_main is None:
    st.stop()

# --- Layout Principal ---
st.title("Análise de Transações e Saúde Financeira")

# --- Seção de Ajuda ---
with st.expander("ℹ️ Entenda as Métricas Principais"):
    st.markdown("""
    - **Momento da Empresa**: Classificação da empresa em uma de quatro fases (Início, Expansão, Maturidade, Declínio), baseada em seu comportamento financeiro e transacional, determinada por um modelo de Machine Learning (K-Means).
    
    - **Fluxo de Caixa Líquido**: A diferença entre o total de dinheiro recebido e o total pago pela empresa. Um indicador chave da saúde financeira (`Total Recebido - Total Pago`).
    
    - **Centralidade de Conexões (Degree)**: Mede a popularidade geral de uma empresa na rede. Quanto maior o valor, mais conectada (pagamentos e recebimentos) a empresa é.

    - **Centralidade de Ponte (Betweenness)**: Indica a frequência com que uma empresa atua como uma "ponte" no caminho mais curto entre outras duas empresas. Empresas com alta centralidade de ponte são importantes para a coesão da rede.

    - **Grupo de Empresas (Comunidade)**: Identifica o cluster de negócios ao qual a empresa pertence, com base na densidade de suas interconexões, detectado pelo algoritmo de Louvain.
    """)

# --- Filtros Globais ---
st.header("Filtros Globais")

# Preparar opções para os filtros
setores_options = ["Todos"] + sorted(df_main['setor_cnae'].unique().tolist())
momentos_options = ["Todos"] + sorted(df_main['momento_empresa'].unique().tolist())
mesano_options = ["Todos"] + sorted(calendario['MesAno'].unique().tolist(), key=lambda x: datetime.strptime(x, "%m/%Y"))

col1, col2, col3 = st.columns(3)

with col1:
    setor_selecionado = st.selectbox("Setor (CNAE)", setores_options)

with col2:
    momento_selecionado = st.selectbox("Momento da Empresa", momentos_options)

with col3:
    mesano_selecionado = st.multiselect("Mês/Ano (DT_REFE)", mesano_options, default=["Todos"])

# --- Aplicação dos Filtros ---
df_filtrado = df_main.copy()
transacoes_filtradas = base_transacoes.copy()

# Filtro por Mês/Ano
if mesano_selecionado and "Todos" not in mesano_selecionado:
    df_filtrado['MesAno'] = df_filtrado['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
    df_filtrado = df_filtrado[df_filtrado['MesAno'].isin(mesano_selecionado)]
    
    transacoes_filtradas['MesAno'] = transacoes_filtradas['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
    transacoes_filtradas = transacoes_filtradas[transacoes_filtradas['MesAno'].isin(mesano_selecionado)]

# Filtro por Setor
if setor_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['setor_cnae'] == setor_selecionado]

# Filtro por Momento da Empresa
if momento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['momento_empresa'] == momento_selecionado]

# --- Sidebar com KPIs ---
with st.sidebar:
    st.image("img/santander logo.jpg")
    st.header("KPIs Globais")

    if not df_filtrado.empty:
        total_recebido = df_filtrado['total_recebido'].sum()
        total_pago = df_filtrado['total_pago'].sum()
        saldo_caixa = total_recebido - total_pago
        transacoes_pagas = df_filtrado['num_transacoes_pagas'].sum()
        transacoes_recebidas = df_filtrado['num_transacoes_recebidas'].sum()
        clientes = df_filtrado['id_empresa'].nunique()
        setores = df_filtrado['setor_cnae'].nunique()
        momentos_contagem = df_filtrado['momento_empresa'].value_counts()
        inicio_count = momentos_contagem.get("INÍCIO", 0)
        maturidade_count = momentos_contagem.get("MATURIDADE", 0)
        expansao_count = momentos_contagem.get("EXPANSÃO", 0)
        declinio_count = momentos_contagem.get("DECLÍNIO", 0)
    else:
        total_recebido = total_pago = saldo_caixa = transacoes_pagas = transacoes_recebidas = clientes = setores = 0
        inicio_count = maturidade_count = expansao_count = declinio_count = 0

    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Recebido</div><div class="kpi-value">{format_currency(total_recebido)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Pago</div><div class="kpi-value">{format_currency(total_pago)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Saldo de Caixa</div><div class="kpi-value">{format_currency(saldo_caixa)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Clientes Únicos</div><div class="kpi-value">{format_number(clientes)}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Empresas por Momento")
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Início</div><div class="kpi-value">{format_number(inicio_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Maturidade</div><div class="kpi-value">{format_number(maturidade_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Expansão</div><div class="kpi-value">{format_number(expansao_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Declínio</div><div class="kpi-value">{format_number(declinio_count)}</div></div>', unsafe_allow_html=True)

# --- Abas de Análise ---
top_n_slider = st.slider("Selecione o Top N para os gráficos", min_value=3, max_value=20, value=10)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Visão Geral", "Início", "Maturidade", "Expansão", "Declínio", "Detalhamento", "Comparar Empresas"])

with tab1:
    display_overview(df_filtrado, df_main, mesano_selecionado, top_n_slider)

with tab2:
    display_inicio(df_filtrado, top_n_slider)

with tab3:
    display_maturidade(df_filtrado, transacoes_filtradas, top_n_slider)

with tab4:
    display_expansao(df_filtrado, top_n_slider, mesano_selecionado)

with tab5:
    display_declinio(df_filtrado, df_main, top_n_slider, mesano_selecionado)

with tab6:
    display_detalhamento(df_filtrado, df_main, base_transacoes, transacoes_filtradas)

with tab7:
    display_comparacao(df_filtrado, df_main)

# --- Botão de Download ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

if not df_filtrado.empty:
    csv = convert_df_to_csv(df_filtrado)
    st.download_button(
       label="Baixar dados filtrados (CSV)",
       data=csv,
       file_name='dados_filtrados.csv',
       mime='text/csv',
    )