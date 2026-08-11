import streamlit as st


def render_accounts_categories(api):
  st.title("Gerenciar Contas e Categorias")

  col_acc, col_cat = st.columns(2)

  with col_acc:
    st.header("Contas Bancárias")
    res_acc = api.get_accounts()

    if res_acc.status_code == 200:
      for acc in res_acc.json():
        c1, c2 = st.columns([3, 1])
        c1.write(
            f"**{acc['name']}** - Saldo: R$"
            f" {acc.get('initial_balance', 0.0):.2f}"
        )
        if c2.button("Excluir", key=f"del_acc_{acc['id']}"):
          api.delete_account(acc["id"])
          st.rerun()

    with st.form("form_acc"):
      st.subheader("Nova Conta")
      acc_name = st.text_input("Nome da Conta")
      acc_bal = st.number_input("Saldo Inicial", value=0.0)
      if st.form_submit_button("Criar Conta"):
        res = api.create_account({"name": acc_name, "initial_balance": acc_bal})
        if res.status_code == 201:
          st.success("Conta criada!")
          st.rerun()

  # --- CATEGORIAS ---
  with col_cat:
    st.header("Categorias")
    res_cat = api.get_categories()

    if res_cat.status_code == 200:
      for cat in res_cat.json():
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{cat['name']}**")
        if c2.button("Excluir", key=f"del_cat_{cat['id']}"):
          api.delete_category(cat["id"])
          st.rerun()

    with st.form("form_cat"):
      st.subheader("Nova Categoria")
      cat_name = st.text_input("Nome da Categoria")
      if st.form_submit_button("Criar Categoria"):
        res = api.create_category({"name": cat_name})
        if res.status_code == 201:
          st.success("Categoria criada!")
          st.rerun()