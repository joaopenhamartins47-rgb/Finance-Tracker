import streamlit as st


def render_profile(api):
  st.title("👤 Configurações do Usuário")

  res_me = api.get_me()
  if res_me.status_code == 200:
    user = res_me.json()
    st.write(f"**Usuário:** {user.get('username')}")
    st.write(f"**E-mail:** {user.get('email')}")

  st.markdown("---")

  with st.form("form_update_user"):
    st.subheader("Atualizar Perfil")
    new_username = st.text_input("Novo Nome de Usuário")
    new_email = st.text_input("Novo E-mail")
    if st.form_submit_button("Atualizar Dados"):
      res = api.update_me({"username": new_username, "email": new_email})
      if res.status_code == 200:
        st.success("Perfil atualizado!")
        st.rerun()
      else:
        st.error("Erro ao atualizar dados.")

  with st.form("form_update_pwd"):
    st.subheader("Alterar Senha")
    old_pwd = st.text_input("Senha Atual", type="password")
    new_pwd = st.text_input("Nova Senha", type="password")
    if st.form_submit_button("Alterar Senha"):
      res = api.update_password(
          {"old_password": old_pwd, "new_password": new_pwd}
      )
      if res.status_code == 200:
        st.success("Senha alterada com sucesso!")
      else:
        st.error("Erro ao alterar senha.")