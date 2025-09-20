# Análise de Momento de Vida da Empresa e Análise de Redes

## Visão Geral do Projeto

Este projeto tem como objetivo principal realizar uma análise detalhada do momento de vida de diversas empresas, utilizando como base seus dados transacionais. Através de técnicas de machine learning e engenharia de features, as empresas são segmentadas em diferentes estágios: **Início, Expansão, Maturidade e Declínio**.

Adicionalmente, é feita uma análise de redes para entender as relações de pagamentos e recebimentos entre as empresas, identificando as mais influentes e as comunidades de negócios existentes.

Os resultados são exportados em dois arquivos CSV, prontos para serem consumidos por ferramentas de visualização de dados como o Power BI.

## Arquivos Gerados

O projeto gera dois arquivos CSV principais, localizados na pasta `data/`:

1.  `dados_para_powerbi.csv`: Contém os dados de cada empresa com as features calculadas e a classificação do seu momento de vida.
2.  `dados_rede_para_powerbi.csv`: Contém as métricas da análise de rede para cada empresa.

---

## Explicação das Colunas de `dados_para_powerbi.csv`

Este arquivo contém as features financeiras e a segmentação de cada empresa.

| Coluna | Descrição | Como foi Calculada |
| :--- | :--- | :--- |
| `id_empresa` | Identificador único da empresa. | Extraído das bases de dados originais. |
| `total_recebido` | Valor monetário total que a empresa recebeu de outras empresas. | Soma de todas as transações onde a empresa é a recebedora. |
| `num_transacoes_recebidas` | Quantidade total de transações de recebimento. | Contagem de todas as transações onde a empresa é a recebedora. |
| `num_clientes_unicos` | Número de clientes únicos que fizeram pagamentos para a empresa. | Contagem de `id_pagador` únicos para a empresa. |
| `total_pago` | Valor monetário total que a empresa pagou para outras empresas. | Soma de todas as transações onde a empresa é a pagadora. |
| `num_transacoes_pagas` | Quantidade total de transações de pagamento. | Contagem de todas as transações onde a empresa é a pagadora. |
| `num_fornecedores_unicos` | Número de fornecedores únicos para quem a empresa fez pagamentos. | Contagem de `id_recebedor` únicos para a empresa. |
| `fluxo_caixa_liquido` | Balanço entre o total recebido e o total pago. | `total_recebido` - `total_pago`. |
| `ticket_medio_recebido` | Valor médio de cada transação de recebimento. | `total_recebido` / `num_transacoes_recebidas`. |
| `ticket_medio_pago` | Valor médio de cada transação de pagamento. | `total_pago` / `num_transacoes_pagas`. |
| `faturamento` | Faturamento declarado da empresa. | Extraído da `Base1_ID.xlsx`. |
| `setor_cnae` | Descrição do setor de atuação da empresa (CNAE). | Extraído da `Base1_ID.xlsx`. |
| `cluster` | Grupo numérico ao qual a empresa foi atribuída pelo modelo de clusterização. | Resultado do algoritmo K-Means (k=4). |
| `momento_empresa` | Classificação do momento de vida da empresa. | Mapeamento do `cluster` para uma das 4 categorias: `Início`, `Expansão`, `Maturidade`, `Declínio`. |

---

## Explicação das Colunas de `dados_rede_para_powerbi.csv`

Este arquivo contém as métricas de centralidade de cada empresa na rede de transações.

| Coluna | Descrição | Como foi Calculada |
| :--- | :--- | :--- |
| `id_empresa` | Identificador único da empresa. | Extraído das bases de dados originais. |
| `Centralidade_de_Conexoes` | Mede a importância geral de uma empresa na rede, com base no número total de conexões (pagamentos e recebimentos). | Calculada usando `degree_centrality` da biblioteca `networkx`. |
| `Centralidade_de_Recebimentos` | Mede a importância de uma empresa como "destino" de pagamentos na rede. | Calculada usando `in_degree_centrality` da biblioteca `networkx`. |
| `Centralidade_de_Pagamentos` | Mede a importância de uma empresa como "origem" de pagamentos na rede. | Calculada usando `out_degree_centrality` da biblioteca `networkx`. |
| `Centralidade_de_Ponte` | Mede a frequência com que uma empresa atua como uma "ponte" ou intermediária no caminho mais curto entre outras duas empresas. | Calculada usando `betweenness_centrality` da biblioteca `networkx`. |
| `Grupo_Empresas` | Identifica a comunidade ou cluster de negócios à qual a empresa pertence, com base na densidade de suas interconexões. | Detectada usando o algoritmo de Louvain (`community_louvain`). |
