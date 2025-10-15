
def generate_recommendations(company_info):
    """
    Gera uma lista de recomendações de ações com base no perfil de uma empresa.

    Args:
        company_info (pd.Series): Uma série contendo os dados da empresa selecionada.

    Returns:
        list: Uma lista de strings, onde cada string é uma recomendação.
    """
    recommendations = []
    momento = company_info.get('momento_empresa', 'N/A')
    fluxo_caixa = company_info.get('fluxo_caixa_liquido', 0)
    
    if momento == 'DECLÍNIO':
        recommendations.append(
            "**Revisão de Custos:** O fluxo de caixa está consistentemente negativo. Recomenda-se uma análise detalhada do `Total Pago` para identificar oportunidades de redução de custos e renegociação com fornecedores."
        )
        recommendations.append(
            "**Retenção de Clientes:** O número de transações e clientes únicos pode estar caindo. Sugere-se focar em estratégias de **retenção** dos clientes atuais, que é mais barato do que adquirir novos."
        )
        recommendations.append(
            "**Análise de Portfólio:** Avalie o portfólio de produtos/serviços para focar nos mais lucrativos e otimizar ou descontinuar os que geram prejuízo, impactando diretamente o `ticket_medio_recebido`."
        )

    elif momento == 'INÍCIO':
        recommendations.append(
            "**Validação de Mercado:** O foco principal deve ser a **aquisição de novos clientes** para validar o modelo de negócio e aumentar a base de receita (`num_clientes_unicos`)."
        )
        recommendations.append(
            "**Gestão de Caixa:** O fluxo de caixa é o ponto mais crítico nesta fase. Mantenha um controle rigoroso sobre as despesas para garantir a sobrevivência e a longevidade da operação."
        )
        if fluxo_caixa > 0:
            recommendations.append(
                "**Reinvestimento Inteligente:** O fluxo de caixa positivo é um ótimo sinal. Considere reinvestir de forma controlada em canais de marketing e vendas que demonstrem maior retorno."
            )

    elif momento == 'EXPANSÃO':
        recommendations.append(
            "**Escalar Operações:** O número de clientes está crescendo rapidamente. Garanta que a operação (logística, atendimento, tecnologia) consiga suportar essa nova demanda para não comprometer a qualidade do serviço."
        )
        recommendations.append(
            "**Otimização do Funil de Vendas:** Aproveite o momento para investir em marketing e vendas e acelerar ainda mais a aquisição de clientes. Monitore o Custo de Aquisição de Cliente (CAC)."
        )
        recommendations.append(
            "**Análise de Rentabilidade:** Analise a rentabilidade dos novos clientes. O `ticket_medio_recebido` está se mantendo ou diminuindo? Foque em adquirir clientes com maior potencial de valor (Lifetime Value)."
        )

    elif momento == 'MATURIDADE':
        recommendations.append(
            "**Inovação e Novos Mercados:** A base de clientes é sólida, mas o crescimento é lento. Busque oportunidades de **inovação** no portfólio de produtos ou explore novos segmentos de mercado para encontrar novas fontes de receita."
        )
        recommendations.append(
            "**Otimização de Processos:** Com um volume alto e estável, o foco deve ser a eficiência. Automatize processos e otimize a estrutura de custos para maximizar a margem de lucro."
        )
        recommendations.append(
            "**Cross-sell e Up-sell:** Aumente o valor de cada cliente (Lifetime Value) através de estratégias de cross-selling (venda de produtos relacionados) e up-selling (venda de versões mais caras do mesmo produto/serviço)."
        )

    if not recommendations:
        recommendations.append("Não há recomendações específicas para o perfil desta empresa no momento. Continue monitorando os KPIs.")

    return recommendations
