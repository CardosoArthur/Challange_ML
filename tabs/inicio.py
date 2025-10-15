
import streamlit as st
import plotly.express as px
from utils.plotting import (
    plot_recebido_vs_pago_mes,
    plot_fluxo_caixa_linha
)

def display_inicio(df_filtrado, top_n_slider):
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
