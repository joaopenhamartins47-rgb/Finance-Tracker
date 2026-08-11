import pandas as pd
import streamlit as st


def render_import_csv(api):
  st.title("Importar Extrato CSV")

  res_accounts = api.get_accounts()
  if res_accounts.status_code != 200:
    st.error("Erro ao carregar contas bancárias.")
    return

  accounts = res_accounts.json()
  acc_map = {acc["name"]: acc["id"] for acc in accounts}

  if not acc_map:
    st.warning("Cadastre ao menos uma conta antes de importar extratos.")
    return

  selected_acc = st.selectbox("Selecione a Conta Destino", list(acc_map.keys()))
  uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

  if uploaded_file:
    # Preview do arquivo
    df_preview = pd.read_csv(uploaded_file)
    st.subheader("Pré-visualização do Arquivo")
    st.dataframe(df_preview.head(5), use_container_width=True)

    if st.button("Confirmar e Importar"):
      uploaded_file.seek(0)
      res = api.import_csv(
          account_id=acc_map[selected_acc],
          file_bytes=uploaded_file.getvalue(),
          filename=uploaded_file.name,
      )

      if res.status_code == 200:
        st.success("Arquivo importado e processado com sucesso!")
      else:
        st.error(f"Erro na importação: {res.text}")