
import streamlit as st
from utils.plotting import (
    plot_empresas_por_momento,
    plot_recebido_vs_pago_mes,
    plot_fluxo_caixa_linha,
    plot_top_setores_recebido
)

def display_overview(df_filtrado, df_main, mesano_selecionado, top_n_slider):
    st.header("Visão Geral do Ecossistema")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_empresas_por_momento(df_filtrado), use_container_width=True)
        st.plotly_chart(plot_fluxo_caixa_linha(df_main if "Todos" in mesano_selecionado else df_filtrado), use_container_width=True, key="fluxo_caixa_geral")
    with col2:
        st.plotly_chart(plot_recebido_vs_pago_mes(df_main if "Todos" in mesano_selecionado else df_filtrado), use_container_width=True, key="recebido_pago_geral")
        st.plotly_chart(plot_top_setores_recebido(df_filtrado, top_n_slider), use_container_width=True, key="top_setores_geral")
