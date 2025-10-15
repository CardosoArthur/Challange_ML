
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def format_currency(value):
    return f"R$ {value:,.2f}"

def format_number(value):
    return f"{value:,.0f}"

def plot_empresas_por_momento(df):
    data = df['momento_empresa'].value_counts().reset_index()
    data.columns = ['momento_empresa', 'clientes']
    fig = px.bar(data, y='momento_empresa', x='clientes', title="Empresas por Momento",
                 orientation='h', text='clientes')
    fig.update_layout(yaxis_title="Momento da Empresa", xaxis_title="Nº de Empresas")
    return fig

def plot_recebido_vs_pago_mes(df):
    df_agg = df.copy()
    if 'DT_REFE' not in df_agg.columns or df_agg['DT_REFE'].isnull().all():
        return go.Figure().update_layout(title="Recebido vs Pago por Mês (Dados insuficientes)")
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
    if 'DT_REFE' not in df_agg.columns or df_agg['DT_REFE'].isnull().all():
        return go.Figure().update_layout(title="Fluxo de Caixa (Linha) (Dados insuficientes)")
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
