
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network
import openpyxl
from datetime import datetime
import calendar
import os

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
        width: 500px;
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

    /* Logo FIAP */
    .logo-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding: 0;
        margin: 0;
    }
    .logo-text {
        font-size: 2rem;
        font-weight: bold;
        color: #C30000;
    }
</style>
""", unsafe_allow_html=True)

# --- Carregamento e Cache dos Dados ---
@st.cache_data
def load_data():
    """
    Carrega, limpa, padroniza, mescla e prepara todos os dataframes para o dashboard.
    Versão final baseada no diagnóstico de colunas.
    """
    try:
        # 1. Leitura dos arquivos
        base_id = pd.read_excel("data/Base1_ID.xlsx")
        base_transacoes = pd.read_excel("data/Base2_Transacoes.xlsx")
        df_powerbi = pd.read_csv("data/dados_para_powerbi.csv", sep=';', encoding='utf-8-sig', decimal=',')
        df_rede = pd.read_csv("data/dados_rede_para_powerbi.csv", sep=';', encoding='utf-8-sig', decimal=',')

        # 2. Padronização de Nomes de Colunas
        for df in [base_id, base_transacoes, df_powerbi, df_rede]:
            df.columns = df.columns.str.strip()

        for df in [base_id, df_powerbi, df_rede]:
            if 'ID' in df.columns:
                df.rename(columns={'ID': 'id_empresa'}, inplace=True)

        # 3. Merge Estratégico e Definitivo
        df_main = df_powerbi

        if 'id_empresa' in base_id.columns:
            date_cols_to_add = ['id_empresa']
            if 'DT_REFE' in base_id.columns: date_cols_to_add.append('DT_REFE')
            if 'DT_ABRT' in base_id.columns: date_cols_to_add.append('DT_ABRT')
            df_main = pd.merge(df_main, base_id[date_cols_to_add], on='id_empresa', how='left')

        if 'id_empresa' in df_rede.columns:
            network_cols_to_add = ['id_empresa', 'Centralidade_de_Conexoes', 'Centralidade_de_Recebimentos', 'Centralidade_de_Pagamentos', 'Centralidade_de_Ponte', 'Grupo_Empresas']
            valid_network_cols = [col for col in network_cols_to_add if col in df_rede.columns]
            df_main = pd.merge(df_main, df_rede[valid_network_cols], on='id_empresa', how='left')

        # 4. Limpeza e Conversão de Tipos
        for col in ['DT_ABRT', 'DT_REFE']:
            if col in df_main.columns:
                df_main[col] = pd.to_datetime(df_main[col], errors='coerce')
        
        for col in ['setor_cnae', 'momento_empresa']:
            if col in df_main.columns:
                df_main[col] = df_main[col].fillna('N/A').astype(str).str.strip().str.upper()

        if 'DS_TRAN' in base_transacoes.columns:
            base_transacoes['DS_TRAN'] = base_transacoes['DS_TRAN'].fillna('N/A').astype(str).str.strip().str.upper()

        # Conversão de colunas numéricas
        numeric_cols = [
            'total_recebido', 'num_transacoes_recebidas', 'num_clientes_unicos',
            'total_pago', 'num_transacoes_pagas', 'num_fornecedores_unicos',
            'fluxo_caixa_liquido', 'ticket_medio_recebido', 'ticket_medio_pago',
            'faturamento', 'Centralidade_de_Conexoes', 'Centralidade_de_Recebimentos',
            'Centralidade_de_Pagamentos', 'Centralidade_de_Ponte'
        ]
        for col in numeric_cols:
            if col in df_main.columns:
                df_main[col] = pd.to_numeric(df_main[col], errors='coerce').fillna(0)

        if 'VL' in base_transacoes.columns:
            base_transacoes['VL'] = pd.to_numeric(base_transacoes['VL'], errors='coerce').fillna(0)

        # 5. Criação da Tabela Calendário
        all_dates = []
        if 'DT_REFE' in base_transacoes.columns:
            all_dates.append(base_transacoes['DT_REFE'].dropna())
        if 'DT_REFE' in df_main.columns:
            all_dates.append(df_main['DT_REFE'].dropna())

        if not all_dates:
            st.error("A coluna 'DT_REFE' é essencial e não foi encontrada.")
            return None, None, None, None

        combined_dates = pd.concat(all_dates)
        min_date, max_date = combined_dates.min(), combined_dates.max()
        
        tabela_calendario = pd.DataFrame(pd.date_range(start=min_date, end=max_date, freq='D'), columns=['Data'])
        tabela_calendario['Ano'] = tabela_calendario['Data'].dt.year
        tabela_calendario['MesNum'] = tabela_calendario['Data'].dt.month
        tabela_calendario['Mes'] = tabela_calendario['Data'].dt.month_name(locale='pt_BR.utf8')
        tabela_calendario['MesAno'] = tabela_calendario['Data'].dt.to_period('M').dt.strftime('%m/%Y')
        tabela_calendario['Dia'] = tabela_calendario['Data'].dt.day

        return df_main, base_id, base_transacoes, tabela_calendario

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar e preparar os dados: {e}")
        return None, None, None, None

# --- Funções de Formatação e Cálculo ---
def format_currency(value):
    return f"R$ {value:,.2f}"

def format_number(value):
    return f"{value:,.0f}"

# --- Carregar os dados ---
df_main, base_id, base_transacoes, calendario = load_data()

if df_main is None:
    st.stop()



# --- Layout Principal ---
st.title("Análise de Transações e Saúde Financeira")

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

    # Cálculos dos KPIs com base nos dados filtrados
    total_recebido = df_filtrado['total_recebido'].sum()
    total_pago = df_filtrado['total_pago'].sum()
    saldo_caixa = total_recebido - total_pago
    transacoes_pagas = df_filtrado['num_transacoes_pagas'].sum()
    transacoes_recebidas = df_filtrado['num_transacoes_recebidas'].sum()
    
    clientes = df_filtrado['id_empresa'].nunique()
    setores = df_filtrado['setor_cnae'].nunique()
    
    # Contagem por momento da empresa
    momentos_contagem = df_filtrado['momento_empresa'].value_counts()
    inicio_count = momentos_contagem.get("INÍCIO", 0)
    maturidade_count = momentos_contagem.get("MATURIDADE", 0)
    expansao_count = momentos_contagem.get("EXPANSÃO", 0)
    declinio_count = momentos_contagem.get("DECLÍNIO", 0)

    # Exibição dos KPIs em cards
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Recebido</div><div class="kpi-value">{format_currency(total_recebido)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Pago</div><div class="kpi-value">{format_currency(total_pago)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Saldo de Caixa</div><div class="kpi-value">{format_currency(saldo_caixa)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Clientes Únicos</div><div class="kpi-value">{format_number(clientes)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Setores Únicos</div><div class="kpi-value">{format_number(setores)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Transações Recebidas</div><div class="kpi-value">{format_number(transacoes_recebidas)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Transações Pagas</div><div class="kpi-value">{format_number(transacoes_pagas)}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Empresas por Momento")
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Início</div><div class="kpi-value">{format_number(inicio_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Maturidade</div><div class="kpi-value">{format_number(maturidade_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Expansão</div><div class="kpi-value">{format_number(expansao_count)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Declínio</div><div class="kpi-value">{format_number(declinio_count)}</div></div>', unsafe_allow_html=True)


# --- Abas de Análise ---
# Slider para Top N
top_n_slider = st.slider("Selecione o Top N para os gráficos", min_value=3, max_value=20, value=10)

# --- Funções para os Gráficos ---
def plot_empresas_por_momento(df):
    data = df['momento_empresa'].value_counts().reset_index()
    data.columns = ['momento_empresa', 'clientes']
    fig = px.bar(data, y='momento_empresa', x='clientes', title="Empresas por Momento",
                 orientation='h', text='clientes')
    fig.update_layout(yaxis_title="Momento da Empresa", xaxis_title="Nº de Empresas")
    return fig

def plot_recebido_vs_pago_mes(df):
    df_agg = df.copy()
    df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
    data = df_agg.groupby('MesAno')[['total_recebido', 'total_pago']].sum().reset_index()
    data['sort_key'] = pd.to_datetime(data['MesAno'], format='%m/%Y')
    data = data.sort_values(by='sort_key').drop(columns='sort_key')
    fig = go.Figure(data=[
        go.Bar(name='Total Recebido', x=data['MesAno'], y=data['total_recebido']),
        go.Bar(name='Total Pago', x=data['MesAno'], y=data['total_pago'])
    ])
    fig.update_layout(barmode='group', title="Recebido vs Pago por Mês",
                      xaxis_title="Mês/Ano", yaxis_title="Valor (R$)")
    return fig

def plot_fluxo_caixa_linha(df):
    df_agg = df.copy()
    df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
    data = df_agg.groupby('MesAno')['fluxo_caixa_liquido'].sum().reset_index()
    data['sort_key'] = pd.to_datetime(data['MesAno'], format='%m/%Y')
    data = data.sort_values(by='sort_key').drop(columns='sort_key')
    fig = px.line(data, x='MesAno', y='fluxo_caixa_liquido', title="Fluxo de Caixa (Linha)",
                  markers=True)
    fig.update_layout(xaxis_title="Mês/Ano", yaxis_title="Fluxo de Caixa (R$)")
    return fig

def plot_top_setores_recebido(df, top_n):
    data = df.groupby('setor_cnae')['total_recebido'].sum().nlargest(top_n).sort_values(ascending=True).reset_index()
    fig = px.bar(data, y='setor_cnae', x='total_recebido', title=f"Top {top_n} Setores por Recebido",
                 orientation='h', text='total_recebido')
    fig.update_traces(texttemplate='%{text:,.2s}')
    fig.update_layout(yaxis_title="Setor", xaxis_title="Total Recebido (R$)")
    return fig

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Visão Geral"

tab_names = ["Visão Geral", "Início", "Maturidade", "Expansão", "Declínio", "Detalhamento"]
st.radio("Navegação", tab_names, key="active_tab", horizontal=True)

if st.session_state.active_tab == "Visão Geral":
    st.header("Visão Geral do Ecossistema")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_empresas_por_momento(df_filtrado), use_container_width=True)
        st.plotly_chart(plot_fluxo_caixa_linha(df_main if "Todos" in mesano_selecionado else df_filtrado), use_container_width=True, key="fluxo_caixa_geral")
    with col2:
        st.plotly_chart(plot_recebido_vs_pago_mes(df_main if "Todos" in mesano_selecionado else df_filtrado), use_container_width=True, key="recebido_pago_geral")
        st.plotly_chart(plot_top_setores_recebido(df_filtrado, top_n_slider), use_container_width=True, key="top_setores_geral")

elif st.session_state.active_tab == "Início":
    st.header("Análise de Empresas em Início")
    df_inicio = df_filtrado[df_filtrado['momento_empresa'] == 'INÍCIO']

    if df_inicio.empty:
        st.warning("Nenhum dado disponível para empresas em 'Início' com os filtros selecionados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            # Setores com mais empresas (Início)
            data_setores = df_inicio['setor_cnae'].value_counts().nlargest(top_n_slider).sort_values(ascending=True).reset_index()
            data_setores.columns = ['setor_cnae', 'clientes']
            fig = px.bar(data_setores, y='setor_cnae', x='clientes', title=f"Top {top_n_slider} Setores com mais empresas (Início)", orientation='h')
            st.plotly_chart(fig, use_container_width=True)

            # Evolução do Fluxo (Início)
            st.plotly_chart(plot_fluxo_caixa_linha(df_inicio), use_container_width=True, key="fluxo_caixa_inicio")

        with col2:
            # Recebido vs Pago (Início)
            st.plotly_chart(plot_recebido_vs_pago_mes(df_inicio), use_container_width=True, key="recebido_pago_inicio")

            # Top 10 Empresas por Recebido (Início)
            data_top_empresas = df_inicio.groupby('id_empresa')['total_recebido'].sum().nlargest(top_n_slider).sort_values(ascending=True).reset_index()
            fig = px.bar(data_top_empresas, y='id_empresa', x='total_recebido', title=f"Top {top_n_slider} Empresas por Recebido (Início)", orientation='h')
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.active_tab == "Maturidade":
    st.header("Análise de Empresas em Maturidade")
    df_maturidade = df_filtrado[df_filtrado['momento_empresa'] == 'MATURIDADE']

    if df_maturidade.empty:
        st.warning("Nenhum dado disponível para empresas em 'Maturidade' com os filtros selecionados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            # Mix por Tipo de Transação
            if not transacoes_filtradas.empty:
                ids_maturidade = df_maturidade['id_empresa'].unique()
                transacoes_maturidade = transacoes_filtradas[transacoes_filtradas['ID_RCBE'].isin(ids_maturidade) | transacoes_filtradas['ID_PGTO'].isin(ids_maturidade)]
                data_mix = transacoes_maturidade.groupby('DS_TRAN')['VL'].sum().reset_index()
                fig = px.pie(data_mix, names='DS_TRAN', values='VL', title="Mix por Tipo de Transação", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            
            # Estabilidade do Fluxo (Razão Receb/Pago)
            df_agg = df_maturidade.copy()
            df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            data_razao = df_agg.groupby('MesAno').agg(total_recebido=('total_recebido', 'sum'), total_pago=('total_pago', 'sum')).reset_index()
            data_razao['razao_receb_pago'] = data_razao['total_recebido'] / data_razao['total_pago'].replace(0, np.nan)
            data_razao['sort_key'] = pd.to_datetime(data_razao['MesAno'], format='%m/%Y')
            data_razao = data_razao.sort_values(by='sort_key').drop(columns='sort_key')
            fig = px.line(data_razao, x='MesAno', y='razao_receb_pago', title="Estabilidade do Fluxo (Razão Receb/Pago)", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Ticket Médio (Recebido x Pago)
            df_agg = df_maturidade.copy()
            df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            data_ticket = df_agg.groupby('MesAno').agg(
                ticket_medio_recebido=('ticket_medio_recebido', 'mean'),
                ticket_medio_pago=('ticket_medio_pago', 'mean')
            ).reset_index()
            data_ticket['sort_key'] = pd.to_datetime(data_ticket['MesAno'], format='%m/%Y')
            data_ticket = data_ticket.sort_values(by='sort_key').drop(columns='sort_key')
            fig = go.Figure(data=[
                go.Bar(name='Ticket Médio Recebido', x=data_ticket['MesAno'], y=data_ticket['ticket_medio_recebido']),
                go.Bar(name='Ticket Médio Pago', x=data_ticket['MesAno'], y=data_ticket['ticket_medio_pago'])
            ])
            fig.update_layout(barmode='group', title="Ticket Médio (Recebido x Pago)", xaxis_title="Mês/Ano", yaxis_title="Valor (R$)")
            st.plotly_chart(fig, use_container_width=True)

            # Top Setores por Recebido (Maturidade)
            st.plotly_chart(plot_top_setores_recebido(df_maturidade, top_n_slider), use_container_width=True, key="top_setores_maturidade")

elif st.session_state.active_tab == "Expansão":
    st.header("Análise de Empresas em Expansão")
    df_expansao = df_filtrado[df_filtrado['momento_empresa'] == 'EXPANSÃO']

    if df_expansao.empty:
        st.warning("Nenhum dado disponível para empresas em 'Expansão' com os filtros selecionados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            df_agg = df_expansao.copy()
            df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            fluxo_mes = df_agg.groupby('MesAno')['fluxo_caixa_liquido'].sum().reset_index()
            fluxo_mes['sort_key'] = pd.to_datetime(fluxo_mes['MesAno'], format='%m/%Y')
            fluxo_mes = fluxo_mes.sort_values(by='sort_key').drop(columns='sort_key')
            fluxo_mes['crescimento_mm_fluxo'] = fluxo_mes['fluxo_caixa_liquido'].pct_change() * 100
            fig = px.line(fluxo_mes, x='MesAno', y='crescimento_mm_fluxo', title="Crescimento % M/M do Fluxo", markers=True)
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig, use_container_width=True)

            # Top 10 Empresas que mais cresceram no mês
            if "Todos" not in mesano_selecionado:
                df_agg_empresa = df_expansao.copy()
                df_agg_empresa['MesAno'] = df_agg_empresa['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
                fluxo_empresa = df_agg_empresa.groupby(['id_empresa', 'MesAno'])['fluxo_caixa_liquido'].sum().unstack()
                crescimento = fluxo_empresa.pct_change(axis='columns').iloc[:, -1].nlargest(top_n_slider).sort_values(ascending=True).reset_index()
                crescimento.columns = ['id_empresa', 'crescimento_mm_fluxo']
                crescimento['crescimento_mm_fluxo'] *= 100
                fig = px.bar(crescimento, y='id_empresa', x='crescimento_mm_fluxo', title=f"Top {top_n_slider} Empresas que mais cresceram no mês", orientation='h')
                fig.update_xaxes(ticksuffix="%")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione um Mês/Ano específico para ver o Top de crescimento.")

        with col2:
            # Volume de Transações
            df_agg = df_expansao.copy()
            df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            data_vol = df_agg.groupby('MesAno')[['num_transacoes_recebidas', 'num_transacoes_pagas']].sum().reset_index()
            data_vol['sort_key'] = pd.to_datetime(data_vol['MesAno'], format='%m/%Y')
            data_vol = data_vol.sort_values(by='sort_key').drop(columns='sort_key')
            fig = go.Figure(data=[
                go.Bar(name='Transações Recebidas', x=data_vol['MesAno'], y=data_vol['num_transacoes_recebidas']),
                go.Bar(name='Transações Pagas', x=data_vol['MesAno'], y=data_vol['num_transacoes_pagas'])
            ])
            fig.update_layout(barmode='group', title="Volume de Transações", xaxis_title="Mês/Ano", yaxis_title="Número de Transações")
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.active_tab == "Declínio":
    st.header("Análise de Empresas em Declínio")
    df_declinio = df_filtrado[df_filtrado['momento_empresa'] == 'DECLÍNIO']

    if df_declinio.empty:
        st.warning("Nenhum dado disponível para empresas em 'Declínio' com os filtros selecionados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            # Variação % 3M do Fluxo
            df_agg = df_declinio.copy()
            df_agg['MesAno'] = df_agg['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            fluxo_mes = df_agg.groupby('MesAno')['fluxo_caixa_liquido'].sum().reset_index()
            fluxo_mes['sort_key'] = pd.to_datetime(fluxo_mes['MesAno'], format='%m/%Y')
            fluxo_mes = fluxo_mes.sort_values(by='sort_key').drop(columns='sort_key')
            fluxo_mes['variacao_3m_fluxo'] = fluxo_mes['fluxo_caixa_liquido'].pct_change(periods=3) * 100
            fig = px.line(fluxo_mes, x='MesAno', y='variacao_3m_fluxo', title="Variação % 3M do Fluxo", markers=True)
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig, use_container_width=True)

            # Setores com maior queda de fluxo
            if "Todos" not in mesano_selecionado:
                df_agg_setor = df_declinio.copy()
                df_agg_setor['MesAno'] = df_agg_setor['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
                fluxo_setor = df_agg_setor.groupby(['setor_cnae', 'MesAno'])['fluxo_caixa_liquido'].sum().unstack().fillna(0)
                if len(fluxo_setor.columns) > 1:
                    fluxo_setor['delta'] = fluxo_setor.iloc[:, -1] - fluxo_setor.iloc[:, -2]
                    data_queda = fluxo_setor.nsmallest(top_n_slider, 'delta').reset_index()
                    fig = px.bar(data_queda, x='setor_cnae', y=data_queda.columns[-2], title="Setores com maior queda de fluxo",
                                 hover_data=['delta'])
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top 10 Empresas por Sequência de Fluxo de Caixa Negativo
            if "Todos" not in mesano_selecionado:
                ids_declinio = df_declinio['id_empresa'].unique()
                df_agg_empresa = df_main[df_main['id_empresa'].isin(ids_declinio)].copy()
                df_agg_empresa['MesAno'] = df_agg_empresa['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
                fluxo_empresa = df_agg_empresa.groupby(['id_empresa', 'MesAno'])['fluxo_caixa_liquido'].sum().unstack().fillna(0)

                def negative_streak(row):
                    streak = 0
                    max_streak = 0
                    for val in row:
                        if val < 0:
                            streak += 1
                        else:
                            max_streak = max(max_streak, streak)
                            streak = 0
                    max_streak = max(max_streak, streak)
                    return max_streak

                streaks = fluxo_empresa.apply(negative_streak, axis=1)
                streaks = streaks.nlargest(top_n_slider).sort_values(ascending=True).reset_index()
                streaks.columns = ['id_empresa', 'negative_cashflow_streak']

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=streaks['negative_cashflow_streak'],
                    y=streaks['id_empresa'],
                    mode='markers',
                    marker_color='red',
                    marker_size=10
                ))

                for i, row in streaks.iterrows():
                    fig.add_shape(
                        type='line',
                        x0=0,
                        y0=i,
                        x1=row['negative_cashflow_streak'],
                        y1=i,
                        line=dict(
                            color="lightgray",
                            width=2,
                        )
                    )

                fig.update_layout(
                    title=f"Top {top_n_slider} Empresas por Sequência de Fluxo de Caixa Negativo",
                    xaxis_title="Meses Consecutivos com Fluxo de Caixa Negativo",
                    yaxis_title="Empresa",
                    yaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(streaks))),
                        ticktext=streaks['id_empresa']
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Selecione um Mês/Ano para ver o ranking de empresas.")

elif st.session_state.active_tab == "Detalhamento":
    st.header("Detalhamento por Empresa")

    empresa_selecionada = st.selectbox(
        "Selecione uma Empresa",
        options=[""] + sorted(df_filtrado['id_empresa'].unique().tolist()),
        format_func=lambda x: f"Empresa {x}" if x else "Selecione..."
    )

    if empresa_selecionada:
        df_empresa = df_filtrado[df_filtrado['id_empresa'] == empresa_selecionada]
        
        # Cards de KPI da empresa
        if not df_empresa.empty:
            info = df_empresa.iloc[0]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Setor (CNAE)", info['setor_cnae'])
            c2.metric("Momento", info['momento_empresa'])
            c3.metric("Total Recebido", format_currency(info['total_recebido']))
            c4.metric("Total Pago", format_currency(info['total_pago']))
            c5.metric("Fluxo de Caixa", format_currency(info['fluxo_caixa_liquido']))

        # Timeline da empresa
        df_empresa_full = df_main[df_main['id_empresa'] == empresa_selecionada]
        df_empresa_full['MesAno'] = df_empresa_full['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
        data_timeline = df_empresa_full.groupby('MesAno').agg(
            total_recebido=('total_recebido', 'sum'),
            total_pago=('total_pago', 'sum')
        ).reset_index()
        data_timeline['sort_key'] = pd.to_datetime(data_timeline['MesAno'], format='%m/%Y')
        data_timeline = data_timeline.sort_values(by='sort_key').drop(columns='sort_key')
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(x=data_timeline['MesAno'], y=data_timeline['total_recebido'], mode='lines+markers', name='Total Recebido'))
        fig_timeline.add_trace(go.Scatter(x=data_timeline['MesAno'], y=data_timeline['total_pago'], mode='lines+markers', name='Total Pago'))
        fig_timeline.update_layout(title="Timeline — Recebido x Pago", xaxis_title="Mês/Ano", yaxis_title="Valor (R$)")
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Tabela de Transações
        st.subheader("Tabela de Transações")
        transacoes_empresa = base_transacoes[
            (base_transacoes['ID_PGTO'] == empresa_selecionada) | 
            (base_transacoes['ID_RCBE'] == empresa_selecionada)
        ]
        st.dataframe(transacoes_empresa)

        # Rede de Transações (PyVis)
        st.subheader("Rede de Transações")
        with st.spinner("Gerando rede de transações..."):
            net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
            
            # Filtrar transações para a rede
            edges_df = transacoes_filtradas[
                (transacoes_filtradas['ID_PGTO'] == empresa_selecionada) | 
                (transacoes_filtradas['ID_RCBE'] == empresa_selecionada)
            ].nlargest(200, 'VL')

            if not edges_df.empty:
                # Adicionar nós e arestas
                for index, row in edges_df.iterrows():
                    src = row['ID_PGTO']
                    dst = row['ID_RCBE']
                    weight = row['VL']
                    
                    net.add_node(src, label=str(src), title=f"Empresa {src}", color="#FF4D4D" if src == empresa_selecionada else "#C30000")
                    net.add_node(dst, label=str(dst), title=f"Empresa {dst}", color="#FF4D4D" if dst == empresa_selecionada else "#00A9E0")
                    net.add_edge(src, dst, value=weight, title=f"Valor: {format_currency(weight)}")

                # Gerar HTML
                net.set_options("""
                var options = {
                  "edges": {
                    "color": {
                      "inherit": true
                    },
                    "smooth": {
                      "enabled": true,
                      "type": "dynamic"
                    }
                  },
                  "physics": {
                    "barnesHut": {
                      "gravitationalConstant": -80000,
                      "springConstant": 0.001,
                      "springLength": 200
                    },
                    "minVelocity": 0.75
                  }
                }
                """)
                
                try:
                    path = '/tmp'
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file_path = os.path.join(path, 'network.html')
                    net.save_graph(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.components.v1.html(html_content, height=610)
                except Exception as e:
                    st.error(f"Não foi possível gerar o gráfico de rede: {e}")
            else:
                st.info("Nenhuma transação encontrada para esta empresa nos filtros atuais para gerar a rede.")

# --- Botão de Download ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df_filtrado)

st.download_button(
   label="Baixar dados filtrados (CSV)",
   data=csv,
   file_name='dados_filtrados.csv',
   mime='text/csv',
)
