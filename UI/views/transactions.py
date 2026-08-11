import pandas as pd
import streamlit as st


def render_transactions(api):
  st.title("💳 Gerenciamento de Transações")

  c1, c2 = st.columns([3, 1])
  with c2:
    if st.button("Classificar Pendentes (IA) 🤖"):
      res_cls = api.classify_pending()
      if res_cls.status_code == 200:
        st.success("Classificação executada com sucesso!")
        st.rerun()
      else:
        st.error("Erro ao classificar transações.")

  res_tx = api.get_transactions()
  res_acc = api.get_accounts()
  res_cat = api.get_categories()

  if res_tx.status_code == 200:
    txs = res_tx.json()
    cats = res_cat.json() if res_cat.status_code == 200 else []
    accs = res_acc.json() if res_acc.status_code == 200 else []

    if txs:
      df = pd.DataFrame(txs)
      cat_map = {c["id"]: c["name"] for c in cats}
      acc_map = {a["id"]: a["name"] for a in accs}

      df["Categoria"] = df["category_id"].map(cat_map)
      df["Conta"] = df["account_id"].map(acc_map)

      # Filtros Rápidos
      search = st.text_input("Buscar por descrição")
      if search:
        df = df[
            df["description"].str.contains(search, case=False, na=False)
        ]

      st.dataframe(df, use_container_width=True)

      # Formulário de Exclusão
      with st.expander("Excluir Transação"):
        tx_id_del = st.number_input("ID da Transação", min_value=1, step=1)
        if st.button("Confirmar Exclusão"):
          res_del = api.delete_transaction(int(tx_id_del))
          if res_del.status_code == 204:
            st.success("Transação removida!")
            st.rerun()
          else:
            st.error("Falha ao excluir transação.")
    else:
      st.info("Nenhuma transação encontrada.")

  # Form de Criar Transação
  with st.expander("➕ Nova Transação Manual"):
    with st.form("form_create_tx"):
      desc = st.text_input("Descrição")
      amount = st.number_input(
          "Valor (Negativo para Despesa, Positivo para Receita)", value=0.0
      )
      acc_dict = (
          {a["name"]: a["id"] for a in res_acc.json()}
          if res_acc.status_code == 200
          else {}
      )
      cat_dict = (
          {c["name"]: c["id"] for c in res_cat.json()}
          if res_cat.status_code == 200
          else {}
      )

      sel_acc = st.selectbox("Conta", list(acc_dict.keys()))
      sel_cat = st.selectbox("Categoria", list(cat_dict.keys()))

      if st.form_submit_button("Salvar Transação"):
        payload = {
            "description": desc,
            "amount": amount,
            "account_id": acc_dict[sel_acc],
            "category_id": cat_dict[sel_cat],
        }
        res_add = api.create_transaction(payload)
        if res_add.status_code == 201:
          st.success("Transação salva!")
          st.rerun()
        else:
          st.error("Erro ao criar transação.")