# regulahub2.0/main.py

import streamlit as st
from database.db_init import init_db, ORGAOS_TITULOS
from database.user_management import check_login, add_user, remove_user, is_admin
from sqlalchemy import create_engine, text
import base64
import os
from datetime import datetime

# =========================
# CONFIGURAÇÃO DO BANCO POSTGRESQL DO RENDER
# =========================
# Pega da variável de ambiente (melhor prática) ou usa URL padrão com :5432 já definido
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://regulahub2_0_db_user:scCy9G4gM9H7ifXD8y2kXrUNvTAIdnSJ"
    "@dpg-d29kvqili9vc73fs2vg0-a.ohio-postgres.render.com:5432/regulahub2_0_db"
)

# Debug – pode remover depois de confirmar
print("Usando DATABASE_URL:", DATABASE_URL)

# Cria a conexão com o banco
engine = create_engine(DATABASE_URL)

# =========================
# CONFIGURAÇÃO STREAMLIT
# =========================
st.set_page_config(page_title="Regulahub", page_icon=":pill:", layout="wide")

css = """
<style>
[data-testid="stHeader"] {
    background-color: #2dbecd;
    background-image: url('app/static/background.png');
    background-size: cover;
    background-position: center 0px;
    background-repeat: no-repeat;
    height: 80px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Logos
sidebar_logo = 'images/MDG_Logo_VMagenta_RGB.png'
full_logo = 'images/VM_VibrantMFilled01_Vpink_Rpurple.png'
st.logo(sidebar_logo, icon_image=full_logo, size='large')

# =========================
# FUNÇÕES AUXILIARES
# =========================
def render_pdf(pdf_data, file_name):
    if pdf_data:
        try:
            # Converte memoryview para bytes, se for o caso
            if isinstance(pdf_data, memoryview):
                pdf_data = pdf_data.tobytes()

            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.download_button("Baixar PDF", data=pdf_data, file_name=file_name, mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao renderizar PDF: {e}")
    else:
        st.warning("Nenhum dado de PDF encontrado para este documento.")

def render_organ_page(orgao):
    try:
        st.markdown(f"<h1 class='organ-title'>{orgao}</h1>", unsafe_allow_html=True)

        if orgao == "ANVISA":
            subtemas = ORGAOS_TITULOS.get(orgao, [])
            if not subtemas:
                st.warning(f"Nenhum subtema configurado para o órgão {orgao}.")
                return
            selected_subtema = st.selectbox("Selecione um Subtema", ["Selecione"] + subtemas, key=f"subtema_{orgao}")
            if selected_subtema == "Selecione":
                return
            st.session_state["selected_subtitulo"] = selected_subtema
            query = text("""
                SELECT id, title, arquivo, data_publicacao 
                FROM documentos 
                WHERE orgao = :orgao AND subtema = :subtema
            """)
            params = {"orgao": orgao, "subtema": selected_subtema}
        else:
            query = text("""
                SELECT id, title, arquivo, data_publicacao 
                FROM documentos 
                WHERE orgao = :orgao AND (subtema IS NULL OR subtema = '')
            """)
            params = {"orgao": orgao}

        with engine.connect() as conn:
            documentos = conn.execute(query, params).fetchall()

        if not documentos:
            st.warning(f"Nenhum documento encontrado para {orgao}.")
            return

        doc_titles = [doc[1] for doc in documentos]
        selected_doc_title = st.selectbox("Selecione um Documento", ["Selecione"] + doc_titles, key=f"doc_{orgao}")
        if selected_doc_title != "Selecione":
            for doc in documentos:
                if doc[1] == selected_doc_title:
                    st.session_state["selected_pdf_id"] = doc[0]
                    st.write(f"Data de Publicação: {doc[3] if doc[3] else 'Não informada'}")
                    render_pdf(doc[2], f"{selected_doc_title}.pdf")
                    break
    except Exception as e:
        st.error(f"Erro: {e}")

def upload_pdf(email):
    st.subheader("Upload de Novo Documento")
    with st.form(key="upload_pdf_form"):
        orgao = st.selectbox("Órgão Regulatório", sorted(ORGAOS_TITULOS.keys()))
        if orgao == "ANVISA":
            subtema = st.selectbox("Subtema", ORGAOS_TITULOS.get(orgao, []))
        else:
            subtema = ""
        title = st.text_input("Título do Documento")
        data_publicacao = st.text_input("Data de Publicação (DD/MM/AAAA)")
        pdf_file = st.file_uploader("Selecione o arquivo PDF", type=["pdf"])
        upload_button = st.form_submit_button("Enviar Documento")

        if upload_button:
            if not orgao or (orgao == "ANVISA" and not subtema) or not title or not pdf_file:
                st.error("Preencha todos os campos obrigatórios.")
            else:
                try:
                    pdf_data = pdf_file.read()
                    filename = pdf_file.name
                    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO documentos 
                            (email, filename, title, arquivo, upload_date, orgao, subtema, data_publicacao)
                            VALUES (:email, :filename, :title, :arquivo, :upload_date, :orgao, :subtema, :data_publicacao)
                        """), {
                            "email": email,
                            "filename": filename,
                            "title": title,
                            "arquivo": pdf_data,
                            "upload_date": upload_date,
                            "orgao": orgao,
                            "subtema": subtema,
                            "data_publicacao": data_publicacao
                        })
                    st.success(f"Documento '{title}' enviado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao enviar documento: {e}")

def render_home():
    st.markdown("<h1 class='page-title'>Bem-vindo ao Regulahub</h1>", unsafe_allow_html=True)
    if os.path.exists("static/images/logo.png"):
        st.image("static/images/logo.png", width=200)
    st.write("Selecione um órgão regulatório na barra lateral para acessar os documentos.")

def render_manage_users():
    st.markdown("<h1 class='page-title'>Gerenciar Usuários</h1>", unsafe_allow_html=True)
    if not is_admin(st.session_state.email):
        st.error("Apenas administradores podem acessar.")
        return
    st.subheader("Usuários Cadastrados")
    with engine.connect() as conn:
        users = conn.execute(text("SELECT email, name, is_admin FROM users")).fetchall()
    if not users:
        st.warning("Nenhum usuário cadastrado.")
    else:
        st.table({
            "E-mail": [u[0] for u in users],
            "Nome": [u[1] for u in users],
            "Papel": ["Admin" if u[2] == 1 else "Usuário" for u in users]
        })
    st.subheader("Adicionar Novo Usuário")
    with st.form(key="add_user_form"):
        new_email = st.text_input("E-mail")
        new_name = st.text_input("Nome")
        new_password = st.text_input("Senha", type="password")
        new_role = st.selectbox("Papel", ["Usuário", "Admin"])
        add_button = st.form_submit_button("Adicionar Usuário")
        if add_button:
            if not new_email or not new_name or not new_password:
                st.error("Preencha todos os campos.")
            else:
                is_admin_val = 1 if new_role == "Admin" else 0
                add_user(new_name, new_email, new_password, is_admin_val)
                st.rerun()
    st.subheader("Remover Usuário")
    with st.form(key="remove_user_form"):
        user_emails = [u[0] for u in users if u[0] != st.session_state.email]
        remove_email = st.selectbox("Selecione o usuário", ["Selecione"] + user_emails)
        remove_button = st.form_submit_button("Remover")
        if remove_button and remove_email != "Selecione":
            remove_user(remove_email)
            st.rerun()
    upload_pdf(st.session_state.email)

def render_sidebar():
    with st.sidebar:
        st.markdown(f"<h3>Bem-vindo, {st.session_state.name}!</h3>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Home"):
            st.session_state.current_page = "Home"
            st.rerun()
        st.markdown("---")
        st.subheader("Órgãos Reguladores")
        for orgao in sorted(ORGAOS_TITULOS.keys()):
            if st.button(orgao, use_container_width=True):
                st.session_state.current_page = orgao
                st.rerun()
        st.markdown("---")
        if is_admin(st.session_state.email):
            if st.button("Gerenciamento"):
                st.session_state.current_page = "Gerenciar Usuários"
                st.rerun()
        if st.button("Sair"):
            st.session_state.clear()
            st.session_state.current_page = "Home"
            st.rerun()

# =========================
# INICIALIZAÇÃO DO APP
# =========================
if not st.session_state.get("logged_in", False):
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_page = "Home"

def main():
    if not st.session_state.logged_in:
        st.title("Login - Regulahub 2.0")
        with st.form(key="login_form"):
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            submit_button = st.form_submit_button("Entrar")
            if submit_button:
                if not email or not password:
                    st.error("Preencha todos os campos.")
                else:
                    name = check_login(email, password)
                    if name:
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.session_state.name = name
                        st.session_state.current_page = "Home"
                        st.success(f"Bem-vindo, {name}!")
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")
    else:
        render_sidebar()
        page = st.session_state.get("current_page", "Home")
        if page == "Home":
            render_home()
        elif page == "Gerenciar Usuários":
            render_manage_users()
        else:
            render_organ_page(page)

if __name__ == "__main__":
    main()

