
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def display_expansao(df_filtrado, top_n_slider, mesano_selecionado):
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
                if len(fluxo_empresa.columns) > 1:
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
