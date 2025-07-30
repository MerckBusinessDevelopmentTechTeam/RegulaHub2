# regulahub2.0/pages/home.py
import streamlit as st
from database.user_management import is_admin
from database.pdf_management import get_pdf_list

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
        st.stop()

    st.title("Regulahub2.0 - Home")
    st.write(f"Bem-vindo, {st.session_state.name}! Gerencie seus documentos regulatórios nas páginas dos órgãos.")

    # Resumo (exemplo: número total de PDFs)
    user_is_admin = is_admin(st.session_state.email)
    pdfs = get_pdf_list(st.session_state.email) if not user_is_admin else get_pdf_list(None)
    st.write(f"**Total de PDFs no sistema**: {len(pdfs)}")

    # Instruções
    st.markdown("""
        Use a barra lateral para navegar até as páginas de cada órgão regulador.
        - **Administradores**: Podem fazer upload e excluir PDFs.
        - **Usuários comuns**: Podem visualizar e baixar PDFs.
    """)

if __name__ == "__main__":
    main()