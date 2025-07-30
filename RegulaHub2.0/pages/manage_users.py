# regulahub2.0/pages/manage_users.py
import streamlit as st
from database.user_management import is_admin, get_users, add_user, delete_user

# Função para carregar CSS
def load_css():
    try:
        with open("static/css/styles.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

def main():
    # Verifica se o usuário está logado
    if not st.session_state.get('logged_in', False):
        st.error("Você precisa fazer login para acessar esta página.")
        st.stop()  # Interrompe a execução da página

    st.title("Regulahub2.0 - Gerenciar Usuários")
    if not is_admin(st.session_state.email):
        st.error("Acesso negado: apenas administradores podem gerenciar usuários.")
        st.stop()

    st.subheader("Criar Novo Usuário")
    with st.form(key="create_user_form"):
        new_name = st.text_input("Nome", placeholder="Digite o nome do usuário")
        new_email = st.text_input("E-mail", placeholder="Digite o e-mail")
        new_password = st.text_input("Senha", type="password", placeholder="Digite a senha")
        is_admin_user = st.checkbox("Tornar usuário administrador")
        create_button = st.form_submit_button("Criar Usuário")
        if create_button:
            if new_name and new_email and new_password:
                add_user(new_name, new_email, new_password, 1 if is_admin_user else 0)
            else:
                st.error("Preencha todos os campos.")

    st.subheader("Usuários Registrados")
    users = get_users()
    if users:
        for user_email, user_is_admin in users:
            col1, col2 = st.columns([3, 1])
            col1.write(f"{user_email} {'(Admin)' if user_is_admin else ''}")
            if user_email != st.session_state.email:
                if col2.button("Excluir", key=f"delete_user_{user_email}"):
                    delete_user(user_email)
                    st.success(f"Usuário {user_email} deletado!")
                    st.rerun()
            else:
                col2.write("(Você)")
    else:
        st.info("Nenhum usuário registrado.")

if __name__ == "__main__":
    main()