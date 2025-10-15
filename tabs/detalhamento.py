
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pyvis.network import Network
import os
from utils.plotting import format_currency
from utils.recommendations import generate_recommendations

def display_detalhamento(df_filtrado, df_main, base_transacoes, transacoes_filtradas):
    st.header("Detalhamento por Empresa")

    empresa_selecionada = st.selectbox(
        "Selecione uma Empresa",
        options=[""] + sorted(df_filtrado['id_empresa'].unique().tolist()),
        format_func=lambda x: f"{x}" if x else "Selecione..."
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

            # --- SEÇÃO DE RECOMENDAÇÕES ---
            st.subheader("💡 Recomendações de Ações")
            recommendations = generate_recommendations(info)
            for rec in recommendations:
                st.info(rec)
            # --- FIM DA SEÇÃO ---

        # Timeline da empresa
        st.subheader("Análise Temporal")
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
            
            edges_df = transacoes_filtradas[
                (transacoes_filtradas['ID_PGTO'] == empresa_selecionada) | 
                (transacoes_filtradas['ID_RCBE'] == empresa_selecionada)
            ].nlargest(200, 'VL')

            if not edges_df.empty:
                for index, row in edges_df.iterrows():
                    src = row['ID_PGTO']
                    dst = row['ID_RCBE']
                    weight = row['VL']
                    
                    net.add_node(src, label=str(src), title=f"Empresa {src}", color="#FF4D4D" if src == empresa_selecionada else "#C30000")
                    net.add_node(dst, label=str(dst), title=f"Empresa {dst}", color="#FF4D4D" if dst == empresa_selecionada else "#00A9E0")
                    net.add_edge(src, dst, value=weight, title=f"Valor: {format_currency(weight)}")

                net.set_options("""
                var options = {
                  "edges": { "color": { "inherit": true }, "smooth": { "enabled": true, "type": "dynamic" }},
                  "physics": { "barnesHut": { "gravitationalConstant": -80000, "springConstant": 0.001, "springLength": 200 }, "minVelocity": 0.75 }
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
