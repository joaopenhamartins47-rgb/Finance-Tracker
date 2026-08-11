import streamlit as st
from api_client import APIClient
from views.account_categories import render_accounts_categories
from views.dashboard import render_dashboard
from views.import_csv import render_import_csv
from views.profile import render_profile
from views.transactions import render_transactions

st.set_page_config(
    page_title="Finance Tracker AI", page_icon="💰", layout="wide"
)

if "token" not in st.session_state:
  st.session_state.token = None

api = APIClient(token=st.session_state.token)

# --- LOGIN / CADASTRO ---
if not st.session_state.token:
  st.title("💰 Personal Finance Tracker")
  t_login, t_reg = st.tabs(["Login", "Criar Conta"])

  with t_login:
    with st.form("login"):
      u = st.text_input("Usuário")
      p = st.text_input("Senha", type="password")
      if st.form_submit_button("Entrar"):
        res = api.login(u, p)
        if res.status_code == 200:
          st.session_state.token = res.json()["access_token"]
          st.rerun()
        else:
          st.error("Credenciais inválidas.")

  with t_reg:
    with st.form("reg"):
      u = st.text_input("Usuário")
      e = st.text_input("E-mail")
      p = st.text_input("Senha", type="password")
      if st.form_submit_button("Cadastrar"):
        res = api.create_user({"username": u, "email": e, "password": p})
        if res.status_code == 201:
          st.success("Conta criada com sucesso!")
        else:
          st.error("Erro ao cadastrar usuário.")

# --- NAVEGAÇÃO AUTENTICADA ---
else:
  st.sidebar.title("Finance Tracker")
  menu = st.sidebar.radio(
      "Menu",
      [
          "Dashboard",
          "Transações",
          "Importar CSV",
          "Contas & Categorias",
          "Meu Perfil",
      ],
  )

  if st.sidebar.button("Sair"):
    st.session_state.token = None
    st.rerun()

  if menu == "Dashboard":
    render_dashboard(api)
  elif menu == "Transações":
    render_transactions(api)
  elif menu == "Importar CSV":
    render_import_csv(api)
  elif menu == "Contas & Categorias":
    render_accounts_categories(api)
  elif menu == "Meu Perfil":
    render_profile(api)