import pandas as pd
import plotly.express as px
import streamlit as st


def render_dashboard(api):
    st.title("📊 Análise de Dados Financeiros e Relatórios")

    # 1. BUSCA DE DADOS NA API
    res_tx = api.get_transactions()
    res_acc = api.get_accounts()
    res_cat = api.get_categories()

    if res_tx.status_code != 200 or not res_tx.json():
        st.info("Nenhuma transação encontrada para gerar análises.")
        return

    tx_data = res_tx.json()
    acc_data = res_acc.json() if res_acc.status_code == 200 else []
    cat_data = res_cat.json() if res_cat.status_code == 200 else []

    # 2. PREPARAÇÃO DO DATAFRAME
    df_tx = pd.DataFrame(tx_data)

    # Tratamento do valor
    df_tx["amount"] = pd.to_numeric(df_tx["amount"], errors="coerce").fillna(0.0)
    df_tx["Valor"] = df_tx["amount"].abs()

    # Resgate da Descrição (suporta 'description' ou 'title' vindo da API)
    if "description" in df_tx.columns:
        df_tx["Descrição"] = df_tx["description"]
    elif "title" in df_tx.columns:
        df_tx["Descrição"] = df_tx["title"]
    else:
        df_tx["Descrição"] = "Sem descrição"

    # Tratamento da Data
    if "transaction_date" in df_tx.columns:
        df_tx["Data"] = pd.to_datetime(df_tx["transaction_date"]).dt.date
    else:
        df_tx["Data"] = pd.Timestamp.today().date()

    # Mapeamento de Categoria
    cat_map = {c["id"]: c["name"] for c in cat_data}

    def extract_category_name(row):
        if isinstance(row.get("category"), dict) and row["category"].get("name"):
            return row["category"]["name"]
        return cat_map.get(row.get("category_id"), "Sem Categoria")

    df_tx["Categoria"] = df_tx.apply(extract_category_name, axis=1)

    # Mapeamento de Conta
    acc_map = {a["id"]: a["name"] for a in acc_data}
    acc_type_map = {a["id"]: a.get("account_type", "checking") for a in acc_data}

    def extract_account_name(row):
        if isinstance(row.get("account"), dict) and row["account"].get("name"):
            return row["account"]["name"]
        return acc_map.get(row.get("account_id"), "Desconhecida")

    df_tx["Conta"] = df_tx.apply(extract_account_name, axis=1)

    def extract_account_type(row):
        if isinstance(row.get("account"), dict) and row["account"].get("account_type"):
            return row["account"]["account_type"]
        return acc_type_map.get(row.get("account_id"), "checking")

    df_tx["Tipo_Conta"] = df_tx.apply(extract_account_type, axis=1)

    # Classificação Cartão de Crédito vs Conta Corrente
    def classify_transaction(row):
        if row["Tipo_Conta"] == "credit_card":
            return "Despesa" if row["amount"] > 0 else "Receita/Pagamento"
        else:
            return "Despesa" if row["amount"] < 0 else "Receita/Pagamento"

    df_tx["Natureza"] = df_tx.apply(classify_transaction, axis=1)

    df_despesas = df_tx[df_tx["Natureza"] == "Despesa"].copy()
    df_receitas = df_tx[df_tx["Natureza"] == "Receita/Pagamento"].copy()

    # 3. CÁLCULO DE MÉTRICAS GERAIS
    total_receita = df_receitas["Valor"].sum()
    total_despesa = df_despesas["Valor"].sum()
    saldo_liquido = total_receita - total_despesa
    taxa_economia = ((saldo_liquido / total_receita * 100) if total_receita > 0 else 0)

    # --- RESUMO GERAL ---
    st.subheader("Resumo Geral")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Receita / Pagamentos", f"R$ {total_receita:,.2f}")
    kpi2.metric("Despesa Total", f"R$ {total_despesa:,.2f}", delta_color="inverse")
    kpi3.metric("Saldo Líquido", f"R$ {saldo_liquido:,.2f}")
    kpi4.metric("Taxa de Poupança", f"{taxa_economia:.1f}%")

    st.markdown("---")

    # --- INSIGHTS DE DESPESAS ---
    st.subheader("💡 Insights de Despesas")
    if not df_despesas.empty:
        maior_gasto = df_despesas["Valor"].max()
        menor_gasto = df_despesas[df_despesas["Valor"] > 0]["Valor"].min()
        media_gasto = df_despesas["Valor"].mean()
        qtd_despesas = len(df_despesas)

        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        col_i1.metric("Maior Gasto Unitário", f"R$ {maior_gasto:,.2f}")
        col_i2.metric("Menor Gasto Unitário", f"R$ {menor_gasto:,.2f}" if pd.notna(menor_gasto) else "R$ 0,00")
        col_i3.metric("Ticket Médio (Gasto)", f"R$ {media_gasto:,.2f}")
        col_i4.metric("Quantidade de Gastos", f"{qtd_despesas} transações")
    else:
        st.info("Não há dados de despesas para gerar insights.")

    st.markdown("---")

    # --- GRÁFICOS TEMPORAIS E VOLUME ---
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("Evolução do Fluxo de Caixa")
        df_fluxo = (df_tx.groupby(["Data", "Natureza"])["Valor"].sum().unstack(fill_value=0))
        if "Despesa" not in df_fluxo.columns:
            df_fluxo["Despesa"] = 0
        if "Receita/Pagamento" not in df_fluxo.columns:
            df_fluxo["Receita/Pagamento"] = 0

        fig_line = px.line(
            df_fluxo,
            markers=True,
            color_discrete_map={"Receita/Pagamento": "#2ECC71", "Despesa": "#E74C3C"},
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_t2:
        st.subheader("Volume Diário (Qtd. de Transações)")
        df_tx_count = df_tx.groupby("Data").size().reset_index(name="Quantidade")
        fig_count = px.bar(
            df_tx_count,
            x="Data",
            y="Quantidade",
            text="Quantidade",
            color_discrete_sequence=["#3498DB"],
        )
        fig_count.update_traces(textposition="outside")
        st.plotly_chart(fig_count, use_container_width=True)

    st.markdown("---")

    # --- RELATÓRIO ANALÍTICO POR CATEGORIA ---
    st.subheader("📑 Relatório Analítico por Categoria (Despesas)")

    if not df_despesas.empty:
        col_r1, col_r2 = st.columns([1, 2])

        with col_r1:
            fig_cat = px.pie(
                df_despesas,
                values="Valor",
                names="Categoria",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_cat.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_cat, use_container_width=True)

        with col_r2:
            df_relatorio_cat = (
                df_despesas.groupby("Categoria")
                .agg(
                    Transações=("Valor", "count"),
                    Gasto_Total=("Valor", "sum"),
                    Maior_Gasto=("Valor", "max"),
                    Média_por_Gasto=("Valor", "mean"),
                )
                .reset_index()
            )

            df_relatorio_cat = df_relatorio_cat.sort_values(by="Gasto_Total", ascending=False)

            for col in ["Gasto_Total", "Maior_Gasto", "Média_por_Gasto"]:
                df_relatorio_cat[col] = df_relatorio_cat[col].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(df_relatorio_cat, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- GRÁFICOS ADICIONAIS ---
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.subheader("Movimentação por Conta (Entradas vs Saídas)")
        # Novo agrupamento lógico: separa por conta e pela natureza da transação
        df_acc_nature = df_tx.groupby(["Conta", "Natureza"])["Valor"].sum().reset_index()

        fig_acc = px.bar(
            df_acc_nature,
            x="Conta",
            y="Valor",
            color="Natureza",
            barmode="group",
            text="Valor",
            color_discrete_map={"Receita/Pagamento": "#2ECC71", "Despesa": "#E74C3C"},
            labels={"Valor": "Volume Movimentado"}
        )
        fig_acc.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
        fig_acc.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_acc, use_container_width=True)

    with col_g4:
        st.subheader("Status da Classificação Automática")
        if "is_classified" in df_tx.columns:
            df_class = df_tx["is_classified"].value_counts().reset_index()
            df_class.columns = ["Status", "Quantidade"]
            df_class["Status"] = df_class["Status"].map(
                {True: "Classificação Automática (Listas)", False: "Manual / Pendente"}
            )

            fig_gauge = px.pie(
                df_class,
                values="Quantidade",
                names="Status",
                color="Status",
                color_discrete_map={
                    "Classificação Automática (Listas)": "#8E44AD",
                    "Manual / Pendente": "#95A5A6",
                },
            )
            fig_gauge.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # --- TABELA DE ANÁLISE INDIVIDUAL ---
    st.subheader("🔍 Análise Individual de Transações")
    st.write(
        "Explore cada transação individualmente. Você pode clicar no cabeçalho das colunas para ordenar (ex: veja tudo que está em 'Outros') ou pesquisar por termos específicos clicando na tabela.")

    # Seleciona apenas as colunas mais úteis para o usuário ler
    colunas_exibicao = ["Data", "Descrição", "Categoria", "Conta", "Natureza", "Valor"]
    df_exibicao = df_tx[colunas_exibicao].copy()

    # Formata a coluna de Valor para ficar mais bonita na tabela
    df_exibicao["Valor"] = df_exibicao["Valor"].apply(lambda x: f"R$ {x:,.2f}")

    # Exibe o dataframe interativo do Streamlit
    st.dataframe(
        df_exibicao.sort_values(by="Data", ascending=False),
        use_container_width=True,
        hide_index=True
    )