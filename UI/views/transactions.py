import streamlit as st
import pandas as pd


def render_transactions(api):
    st.title(" Gerenciamento de Transações")

    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Classificar Pendentes (IA) "):
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
            cat_map = {c["id"]: c["name"] for c in cats}
            acc_map = {a["id"]: a["name"] for a in accs}

            # Garante que IDs vindos como string também funcionem.
            cat_map_normalized = {str(k): v for k, v in cat_map.items()}
            acc_map_normalized = {str(k): v for k, v in acc_map.items()}

            cat_dict = {c["name"]: c["id"] for c in cats}
            cat_names = list(cat_dict.keys())

            search = st.text_input("Buscar por descrição")

            if search:
                txs = [
                    tx for tx in txs
                    if search.lower() in str(tx.get("description", "")).lower()
                ]

            st.write("### Lista de Transações")
            st.caption("Use  para alterar a categoria de uma transação, inclusive as classificadas como 'Outros'.")

            # Cabeçalho da tabela
            h1, h2, h3, h4, h5, h6 = st.columns([1.3, 3, 1.5, 2, 2, 1.2])
            h1.write("**Data**")
            h2.write("**Descrição**")
            h3.write("**Valor**")
            h4.write("**Categoria**")
            h5.write("**Conta**")
            h6.write("**Ações**")
            st.divider()

            for tx in txs:
                col1, col2, col3, col4, col5, col6 = st.columns([1.3, 3, 1.5, 2, 2, 1.2])

                col1.write(tx.get("transaction_date", ""))
                col2.write(tx.get("description", ""))

                valor = float(tx.get("amount", 0))
                cor = "red" if valor < 0 else "green"
                col3.markdown(
                    f"<span style='color:{cor}'>R$ {valor:,.2f}</span>",
                    unsafe_allow_html=True,
                )

                current_category_id = tx.get("category_id")
                current_category_name = cat_map_normalized.get(
                    str(current_category_id), "Sem Categoria"
                )
                col4.write(current_category_name)

                account_id = tx.get("account_id")
                col5.write(acc_map_normalized.get(str(account_id), "N/A"))

                # Editar categoria
                if col6.button("", key=f"edit_cat_{tx['id']}", help="Editar categoria"):
                    st.session_state[f"editing_cat_{tx['id']}"] = True

                # Excluir
                if col6.button("", key=f"del_tx_{tx['id']}", help="Excluir transação"):
                    res_del = api.delete_transaction(tx["id"])
                    if res_del.status_code in [200, 204]:
                        st.success("Transação removida!")
                        st.rerun()
                    else:
                        st.error(f"Falha ao excluir: {res_del.text}")

                # Editor exibido apenas para a transação selecionada
                if st.session_state.get(f"editing_cat_{tx['id']}", False):
                    with st.container(border=True):
                        st.write(f"**Alterar categoria:** {tx.get('description', 'Sem descrição')}")

                        current_index = (
                            cat_names.index(current_category_name)
                            if current_category_name in cat_names
                            else 0
                        )

                        new_category_name = st.selectbox(
                            "Nova categoria",
                            cat_names,
                            index=current_index,
                            key=f"new_cat_{tx['id']}",
                        )

                        save_col, cancel_col = st.columns(2)

                        with save_col:
                            if st.button("Salvar categoria", key=f"save_cat_{tx['id']}", type="primary"):
                                new_category_id = cat_dict[new_category_name]
                                payload = {"category_id": new_category_id}

                                try:
                                    res_update = api.update_transaction(tx["id"], payload)
                                except AttributeError:
                                    res_update = None

                                if res_update is None:
                                    st.error(
                                        "O frontend está pronto, mas o APIClient ainda não possui "
                                        "update_transaction(). Preciso do backend/APIClient para ligar a gravação."
                                    )
                                elif res_update.status_code in [200, 204]:
                                    st.session_state.pop(f"editing_cat_{tx['id']}", None)
                                    st.success("Categoria da transação atualizada!")
                                    st.rerun()
                                else:
                                    st.error(
                                        f"Erro ao atualizar categoria ({res_update.status_code}): "
                                        f"{res_update.text}"
                                    )

                        with cancel_col:
                            if st.button("Cancelar", key=f"cancel_cat_{tx['id']}"):
                                st.session_state.pop(f"editing_cat_{tx['id']}", None)
                                st.rerun()

            st.divider()
        else:
            st.info("Nenhuma transação encontrada.")

    # Formulário de criar transação
    with st.expander("Nova Transação Manual"):
        with st.form("form_create_tx"):
            desc = st.text_input("Descrição")
            amount = st.number_input(
                "Valor (Negativo para Despesa, Positivo para Receita)",
                value=0.0,
            )

            acc_dict = {
                a["name"]: a["id"]
                for a in (res_acc.json() if res_acc.status_code == 200 else [])
            }
            cat_dict = {
                c["name"]: c["id"]
                for c in (res_cat.json() if res_cat.status_code == 200 else [])
            }

            sel_acc = st.selectbox("Conta", list(acc_dict.keys())) if acc_dict else None
            sel_cat = st.selectbox("Categoria", list(cat_dict.keys())) if cat_dict else None

            if st.form_submit_button("Salvar Transação"):
                if sel_acc and sel_cat:
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
                else:
                    st.warning(
                        "Crie ao menos uma Conta e uma Categoria antes de adicionar transações."
                    )