
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def display_declinio(df_filtrado, df_main, top_n_slider, mesano_selecionado):
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
