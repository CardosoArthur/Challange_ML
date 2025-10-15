
import streamlit as st
import pandas as pd
from utils.plotting import format_currency, format_number
import plotly.graph_objects as go

def display_comparacao(df_filtrado, df_main):
    st.header("Comparar Empresas")

    empresas_selecionadas = st.multiselect(
        "Selecione até 3 empresas para comparar",
        options=sorted(df_filtrado['id_empresa'].unique().tolist()),
        max_selections=3
    )

    if empresas_selecionadas:
        df_comparacao = df_filtrado[df_filtrado['id_empresa'].isin(empresas_selecionadas)]
        
        cols = st.columns(len(empresas_selecionadas))

        for i, empresa_id in enumerate(empresas_selecionadas):
            with cols[i]:
                st.subheader(f"{empresa_id}")
                info = df_comparacao[df_comparacao['id_empresa'] == empresa_id].iloc[0]

                st.metric("Momento", info['momento_empresa'])
                st.metric("Setor", info['setor_cnae'])
                st.metric("Faturamento", format_currency(info['faturamento']))
                st.metric("Fluxo de Caixa", format_currency(info['fluxo_caixa_liquido']))
                st.metric("Total Recebido", format_currency(info['total_recebido']))
                st.metric("Total Pago", format_currency(info['total_pago']))
                st.metric("Ticket Médio Recebido", format_currency(info['ticket_medio_recebido']))
                st.metric("Ticket Médio Pago", format_currency(info['ticket_medio_pago']))

        st.subheader("Timeline de Fluxo de Caixa Líquido")
        fig_timeline = go.Figure()

        for empresa_id in empresas_selecionadas:
            df_empresa_full = df_main[df_main['id_empresa'] == empresa_id]
            df_empresa_full['MesAno'] = df_empresa_full['DT_REFE'].dt.to_period('M').dt.strftime('%m/%Y')
            data_timeline = df_empresa_full.groupby('MesAno')['fluxo_caixa_liquido'].sum().reset_index()
            data_timeline['sort_key'] = pd.to_datetime(data_timeline['MesAno'], format='%m/%Y')
            data_timeline = data_timeline.sort_values(by='sort_key').drop(columns='sort_key')
            
            fig_timeline.add_trace(go.Scatter(x=data_timeline['MesAno'], y=data_timeline['fluxo_caixa_liquido'], mode='lines+markers', name=empresa_id))
        
        fig_timeline.update_layout(xaxis_title="Mês/Ano", yaxis_title="Valor (R$)")
        st.plotly_chart(fig_timeline, use_container_width=True)
