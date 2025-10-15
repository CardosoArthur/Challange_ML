
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.plotting import plot_top_setores_recebido

def display_maturidade(df_filtrado, transacoes_filtradas, top_n_slider):
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
                if not transacoes_maturidade.empty:
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
