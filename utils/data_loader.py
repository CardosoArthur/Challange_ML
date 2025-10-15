
import streamlit as st
import pandas as pd
import os

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
            base_transacoes['DT_REFE'] = pd.to_datetime(base_transacoes['DT_REFE'], errors='coerce')
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

    except FileNotFoundError as e:
        st.error(f"Erro: Arquivo não encontrado. Verifique o caminho: {e.filename}")
        return None, None, None, None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar e preparar os dados: {e}")
        return None, None, None, None
