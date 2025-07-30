# regulahub2.0/pages/abnt.py
import streamlit as st
import base64
from database.db_init import ORGAOS_TITULOS
from database.user_management import is_admin
from database.pdf_management import save_pdf_to_db, get_pdf_list, read_pdf_from_db, delete_pdf
from io import BytesIO

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

    st.title("Regulahub2.0 - POLÍCIA FEDERAL")
    st.write("Gerencie documentos regulatórios da POLÍCIA FEDERAL.")

    orgao = "POLÍCIA FEDERAL"
    subtitulos = ORGAOS_TITULOS.get(orgao, [])
    user_is_admin = is_admin(st.session_state.email)

    # Seleção de subtítulo
    if subtitulos:
        selected_subtitulo = st.selectbox(
            "Selecione um subtítulo",
            subtitulos,
            key=f"subtitulo_{orgao}",
            help="Escolha o subtítulo para visualizar ou anexar PDFs"
        )

        # Upload de PDFs (apenas administradores)
        if user_is_admin:
            st.subheader(f"Anexar PDF em {selected_subtitulo}")
            pdf_title = st.text_input(
                "Título do PDF (opcional)",
                key=f"pdf_title_{orgao}",
                placeholder="Deixe em branco para usar o nome do arquivo"
            )
            uploaded_file = st.file_uploader(
                "Escolha um PDF",
                type=["pdf"],
                key=f"upload_{orgao}"
            )
            if uploaded_file and st.button("Salvar PDF", key=f"save_{orgao}"):
                if save_pdf_to_db(st.session_state.email, uploaded_file, orgao, selected_subtitulo, pdf_title):
                    st.success(f"PDF '{pdf_title or uploaded_file.name}' anexado com sucesso!")
                    st.rerun()
                else:
                    st.error("Falha ao anexar o PDF.")

        # Lista de PDFs
        st.subheader(f"PDFs em {selected_subtitulo}")
        pdfs = get_pdf_list(st.session_state.email, topic=orgao, subtopic=selected_subtitulo)
        if pdfs:
            for pdf_id, filename, title, upload_date, topic, subtopic in pdfs:
                display_title = title or filename
                col1, col2 = st.columns([3, 1])
                if col1.button(
                    f"{display_title} ({upload_date})",
                    key=f"pdf_{orgao}_{subtopic}_{pdf_id}"
                ):
                    st.session_state.selected_pdf_id = pdf_id
                    st.session_state.selected_orgao = orgao
                    st.session_state.selected_subtitulo = subtopic
                    st.rerun()
                if user_is_admin and col2.button("Excluir", key=f"delete_pdf_{orgao}_{subtopic}_{pdf_id}"):
                    delete_pdf(pdf_id)
                    st.success(f"PDF '{display_title}' excluído!")
                    st.rerun()
        else:
            st.info("Nenhum PDF anexado neste subtítulo.")

    # Exibir PDF selecionado
    if st.session_state.get('selected_pdf_id'):
        pdf_id = st.session_state.selected_pdf_id
        orgao = st.session_state.get('selected_orgao', 'Desconhecido')
        subtitulo = st.session_state.get('selected_subtitulo', 'Desconhecido')
        st.subheader(f"Visualizando: {orgao} - {subtitulo}")
        pdf_file = read_pdf_from_db(pdf_id)
        if pdf_file:
            conn = sqlite3.connect("regulahub2.0.db")
            c = conn.cursor()
            c.execute("SELECT filename, title FROM pdfs WHERE id = ?", (pdf_id,))
            filename, title = c.fetchone()
            conn.close()
            display_title = title or filename
            st.write(f"**Título**: {display_title}")
            st.write(f"**Arquivo**: {filename}")
            st.write(f"**Órgão**: {orgao}")
            st.write(f"**Subtítulo**: {subtitulo}")
            pdf_data = pdf_file.getvalue()
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.download_button(
                label="Baixar PDF",
                data=pdf_file,
                file_name=filename,
                mime="application/pdf",
                key=f"download_{orgao}_{subtitulo}_{pdf_id}"
            )
            if user_is_admin and st.button("Excluir PDF", key=f"delete_pdf_main_{pdf_id}"):
                delete_pdf(pdf_id)
                st.session_state.selected_pdf_id = None
                st.session_state.selected_orgao = None
                st.session_state.selected_subtitulo = None
                st.success(f"PDF '{display_title}' excluído!")
                st.rerun()
            # Placeholder para integração de IA
            if st.button("Analisar com IA", key=f"analyze_{pdf_id}"):
                st.info("Funcionalidade de análise de IA ainda não implementada.")

if __name__ == "__main__":
    main()