# regulahub2.0/main.py
import streamlit as st
from database.db_init import init_db, ORGAOS_TITULOS
from database.user_management import check_login, add_user, remove_user, is_admin
import sqlite3
import base64
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Regulahub 2.0", page_icon=":pill:", layout="wide")

css = """
<style>
[data-testid="stHeader"] {
    background-color: #2dbecd; /* Cor de fallback */
    background-image: url('app/static/background.png'); /* Caminho corrigido */
    background-size: cover;
    background-position: center 0px;
    background-repeat: no-repeat;
    height: 80px;
}
</style>
"""

# Injetar o CSS
st.markdown(css, unsafe_allow_html=True)

# Logo
sidebar_logo = 'images/MDG_Logo_VMagenta_RGB.png'
full_logo = 'images/VM_VibrantMFilled01_Vpink_Rpurple.png'

st.logo(sidebar_logo, icon_image=full_logo, size='large')

# Função para renderizar PDF
def render_pdf(pdf_data, file_name):
    if pdf_data:
        try:
            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.download_button("Baixar PDF", data=pdf_data, file_name=file_name, mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao renderizar PDF: {e}")
    else:
        st.warning("Nenhum dado de PDF encontrado para este documento.")

# Função para renderizar página de órgão
def render_organ_page(orgao):
    try:
        st.markdown(f"<h1 class='organ-title'>{orgao}</h1>", unsafe_allow_html=True)
        conn = sqlite3.connect("regulahub2.0.db")
        c = conn.cursor()

        # Verifica se o órgão é ANVISA (que possui subtemas)
        if orgao == "ANVISA":
            subtemas = ORGAOS_TITULOS.get(orgao, [])
            if not subtemas:
                st.warning(f"Nenhum subtema configurado para o órgão {orgao}.")
                conn.close()
                return

            selected_subtema = st.selectbox("Selecione um Subtema", ["Selecione"] + subtemas, key=f"subtema_{orgao}")
            if selected_subtema == "Selecione":
                conn.close()
                return

            st.session_state["selected_subtitulo"] = selected_subtema
            c.execute("SELECT id, title, arquivo, data_publicacao FROM documentos WHERE orgao = ? AND subtema = ?", (orgao, selected_subtema))
        else:
            # Para outros órgãos, busca documentos sem subtema (ou com subtema NULL/vazio)
            c.execute("SELECT id, title, arquivo, data_publicacao FROM documentos WHERE orgao = ? AND (subtema IS NULL OR subtema = '')", (orgao,))

        documentos = c.fetchall()
        conn.close()

        if not documentos:
            st.warning(f"Nenhum documento encontrado para {'o subtema ' + selected_subtema if orgao == 'ANVISA' else 'o órgão ' + orgao}.")
            return

        doc_titles = [doc[1] for doc in documentos]
        selected_doc_title = st.selectbox("Selecione um Documento", ["Selecione"] + doc_titles, key=f"doc_{orgao}")
        if selected_doc_title != "Selecione":
            st.session_state["selected_pdf_id"] = next(doc[0] for doc in documentos if doc[1] == selected_doc_title)
            for doc in documentos:
                if doc[1] == selected_doc_title:
                    st.write(f"Data de Publicação: {doc[3] if doc[3] else 'Não informada'}")
                    render_pdf(doc[2], f"{selected_doc_title}.pdf")
                    break
    except sqlite3.OperationalError as e:
        st.error(f"Erro no banco de dados: {e}")
        st.write("Verifique se a tabela 'documentos' existe e contém as colunas 'id', 'title', 'arquivo', 'orgao', 'subtema', e 'data_publicacao'.")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")

# Função para upload de PDFs (apenas para administradores)
def upload_pdf(email):
    st.subheader("Upload de Novo Documento")
    with st.form(key="upload_pdf_form"):
        orgao = st.selectbox("Órgão Regulatório", sorted(ORGAOS_TITULOS.keys()))
        if orgao == "ANVISA":
            subtema = st.selectbox("Subtema", ORGAOS_TITULOS.get(orgao, []))
        else:
            subtema = ""  # Para outros órgãos, subtema é vazio
        title = st.text_input("Título do Documento", placeholder="Digite o título do documento")
        data_publicacao = st.text_input("Data de Publicação (DD/MM/AAAA)", placeholder="Ex.: 01/01/2025")
        pdf_file = st.file_uploader("Selecione o arquivo PDF", type=["pdf"])
        upload_button = st.form_submit_button("Enviar Documento")

        if upload_button:
            if not orgao or (orgao == "ANVISA" and not subtema) or not title or not pdf_file:
                st.error("Preencha todos os campos obrigatórios.")
            else:
                try:
                    # Lê o arquivo PDF como binário
                    pdf_data = pdf_file.read()
                    filename = pdf_file.name
                    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Insere no banco de dados
                    conn = sqlite3.connect("regulahub2.0.db")
                    c = conn.cursor()
                    c.execute('''INSERT INTO documentos (email, filename, title, arquivo, upload_date, orgao, subtema, data_publicacao)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                             (email, filename, title, pdf_data, upload_date, orgao, subtema, data_publicacao))
                    conn.commit()
                    conn.close()
                    st.success(f"Documento '{title}' enviado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao enviar documento: {e}")

# Função para renderizar a página Home
def render_home():
    st.markdown("<h1 class='page-title'>Bem-vindo ao Regulahub 2.0</h1>", unsafe_allow_html=True)
    if os.path.exists("static/images/logo.png"):
        st.image("static/images/logo.png", width=200)
    st.write("Selecione um órgão regulatório na barra lateral para acessar os documentos.")

# Função para renderizar a página de gerenciamento de usuários
def render_manage_users():
    st.markdown("<h1 class='page-title'>Gerenciar Usuários</h1>", unsafe_allow_html=True)

    if not is_admin(st.session_state.email):
        st.error("Acesso negado. Apenas administradores podem gerenciar usuários.")
        return

    st.subheader("Usuários Cadastrados")
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    c.execute("SELECT email, name, is_admin FROM users")
    users = c.fetchall()
    conn.close()

    if not users:
        st.warning("Nenhum usuário cadastrado.")
    else:
        st.table({"E-mail": [u[0] for u in users], "Nome": [u[1] for u in users], "Papel": ["Admin" if u[2] == 1 else "Usuário" for u in users]})

    st.subheader("Adicionar Novo Usuário")
    with st.form(key="add_user_form"):
        new_email = st.text_input("E-mail", placeholder="Digite o e-mail do novo usuário")
        new_name = st.text_input("Nome", placeholder="Digite o nome do usuário")
        new_password = st.text_input("Senha", type="password", placeholder="Digite a senha")
        new_role = st.selectbox("Papel", ["Usuário", "Admin"], index=0)
        add_button = st.form_submit_button("Adicionar Usuário")

        if add_button:
            if not new_email or not new_name or not new_password:
                st.error("Preencha todos os campos.")
            else:
                try:
                    is_admin_value = 1 if new_role == "Admin" else 0
                    add_user(new_name, new_email, new_password, is_admin_value)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar usuário: {e}")

    st.subheader("Remover Usuário")
    with st.form(key="remove_user_form"):
        user_emails = [u[0] for u in users if u[0] != st.session_state.email]
        remove_email = st.selectbox("Selecione o E-mail do Usuário", ["Selecione"] + user_emails)
        remove_button = st.form_submit_button("Remover Usuário")

        if remove_button and remove_email != "Selecione":
            try:
                remove_user(remove_email)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao remover usuário: {e}")

    upload_pdf(st.session_state.email)

# Função para renderizar a sidebar
def render_sidebar():
    with st.sidebar:
        st.markdown(f"<h3 class='sidebar-title'>Bem-vindo, {st.session_state.name}!</h3>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Home", key="home_button"):
            st.session_state.current_page = "Home"
            st.session_state.selected_pdf_id = None
            st.session_state.selected_orgao = None
            st.session_state.selected_subtitulo = None
            st.rerun()
        st.markdown("---")
        st.subheader("Órgãos Regulatórios")
        for orgao in sorted(ORGAOS_TITULOS.keys()):
            if st.button(orgao, key=f"orgao_{orgao}"):
                st.session_state.current_page = orgao
                st.session_state.selected_pdf_id = None
                st.session_state.selected_orgao = orgao
                st.session_state.selected_subtitulo = None
                st.rerun()
        st.markdown("---")
        if is_admin(st.session_state.email):
            if st.button("Gerenciamento", key="manage_users_button"):
                st.session_state.current_page = "Gerenciar Usuários"
                st.session_state.selected_pdf_id = None
                st.session_state.selected_orgao = None
                st.session_state.selected_subtitulo = None
                st.rerun()
        if st.button("Sair", key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.name = ""
            st.session_state.selected_pdf_id = None
            st.session_state.selected_orgao = None
            st.session_state.selected_subtitulo = None
            st.session_state.current_page = "Home"
            st.rerun()

# Oculta a sidebar para usuários não logados
if not st.session_state.get("logged_in", False):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )

# Inicializa o banco de dados
init_db()

# Estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.name = ""
    st.session_state.selected_pdf_id = None
    st.session_state.selected_orgao = None
    st.session_state.selected_subtitulo = None
    st.session_state.current_page = "Home"

# Interface principal
def main():
    if not st.session_state.logged_in:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.title("Regulahub 2.0 - Login")
        st.write("Acesse sua conta para gerenciar documentos regulatórios.")
        with st.form(key="login_form"):
            email = st.text_input("E-mail", placeholder="Digite seu e-mail")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
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
        st.markdown("</div>", unsafe_allow_html=True)
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