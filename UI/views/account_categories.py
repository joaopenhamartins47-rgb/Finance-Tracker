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
                    f"**{acc['name']}** — {'Cartão de Crédito' if acc['account_type'] == 'credit_card' else 'Conta Corrente'}")

                with c2.popover("Excluir"):
                    st.warning("⚠️ **Atenção:** Apagar esta conta excluirá **todas as transações** associadas a ela!")
                    if st.button("Confirmar Exclusão", key=f"confirm_del_acc_{acc['id']}", type="primary"):
                        res_del = api.delete_account(acc["id"])
                        if res_del.status_code in [200, 204]:
                            st.success("Conta e transações vinculadas excluídas!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao excluir conta ({res_del.status_code}): {res_del.text}")

        with st.form("form_acc"):
            st.subheader("Nova Conta")
            acc_name = st.text_input("Nome da Conta (mínimo 3 caracteres)")
            acc_type_label = st.selectbox("Tipo de Conta", ["Conta Corrente", "Cartão de Crédito"])
            acc_type = "checking" if acc_type_label == "Conta Corrente" else "credit_card"
            if st.form_submit_button("Criar Conta"):
                res = api.create_account({"name": acc_name, "account_type": acc_type})
                if res.status_code == 201:
                    st.success("Conta criada!")
                    st.rerun()
                else:
                    st.error(f"Erro ao criar conta ({res.status_code}): {res.text}")

    with col_cat:
        st.header("Categorias")
        res_cat = api.get_categories()

        if res_cat.status_code == 200:
            for cat in res_cat.json():
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{cat['name']}**")
                if c2.button("Excluir", key=f"del_cat_{cat['id']}"):
                    res_del = api.delete_category(cat["id"])
                    if res_del.status_code in [200, 204]:
                        st.success("Categoria excluída!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao excluir categoria ({res_del.status_code}): {res_del.text}")

        with st.form("form_cat"):
            st.subheader("Nova Categoria")
            cat_name = st.text_input("Nome da Categoria")
            if st.form_submit_button("Criar Categoria"):
                res = api.create_category({"name": cat_name})
                if res.status_code == 201:
                    st.success("Categoria criada!")
                    st.rerun()
                else:
                    st.error(f"Erro ao criar categoria ({res.status_code}): {res.text}")