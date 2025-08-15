# regulahub2.0/pages/anvisa.py

import streamlit as st
import base64
from database.db_init import ORGAOS_TITULOS
from database.user_management import is_admin
from database.pdf_management import (
    save_pdf_to_db,
    get_pdf_list,
    read_pdf_from_db,
    delete_pdf
)

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

    st.title("Regulahub2.0 - ANVISA")
    st.write("Gerencie documentos regulatórios da ANVISA.")

    orgao = "ANVISA"
    subtitulos = ORGAOS_TITULOS.get(orgao, [])
    user_is_admin = is_admin(st.session_state.email)

    # ========= Seleção de subtema =========
    selected_subtitulo = None
    if subtitulos:
        selected_subtitulo = st.selectbox(
            "Selecione um Subtema",
            subtitulos,
            key=f"subtema_{orgao}",
            help="Escolha o subtítulo para visualizar ou anexar PDFs"
        )

    # ========= Upload de PDFs (apenas admin) =========
    if user_is_admin and selected_subtitulo:
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
            if save_pdf_to_db(
                st.session_state.email,
                uploaded_file,
                orgao,
                selected_subtitulo,  # aqui vai o subtema
                pdf_title
            ):
                st.success(f"PDF '{pdf_title or uploaded_file.name}' anexado com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao anexar o PDF.")

    # ========= Lista de PDFs =========
    if selected_subtitulo:
        st.subheader(f"PDFs em {selected_subtitulo}")
        pdfs = get_pdf_list(
            st.session_state.email,
            topic=orgao,
            subtopic=selected_subtitulo
        )

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

                if user_is_admin and col2.button(
                    "Excluir",
                    key=f"delete_pdf_{orgao}_{subtopic}_{pdf_id}"
                ):
                    delete_pdf(pdf_id)
                    st.success(f"PDF '{display_title}' excluído!")
                    st.rerun()
        else:
            st.info("Nenhum PDF anexado neste subtítulo.")

    # ========= Exibir PDF selecionado =========
    if st.session_state.get('selected_pdf_id'):
        pdf_id = st.session_state.selected_pdf_id
        orgao_sel = st.session_state.get('selected_orgao', orgao)
        subtitulo_sel = st.session_state.get('selected_subtitulo', 'Desconhecido')
        st.subheader(f"Visualizando: {orgao_sel} - {subtitulo_sel}")

        pdf_file, filename, title = read_pdf_from_db(pdf_id)

        if pdf_file:
            # Converte memoryview para bytes, se necessário
            if isinstance(pdf_file, memoryview):
                pdf_file = pdf_file.tobytes()

            display_title = title or filename

            st.write(f"**Título**: {display_title}")
            st.write(f"**Arquivo**: {filename}")
            st.write(f"**Órgão**: {orgao_sel}")
            st.write(f"**Subtítulo**: {subtitulo_sel}")

            base64_pdf = base64.b64encode(pdf_file).decode('utf-8')
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                f'width="700" height="500" type="application/pdf"></iframe>',
                unsafe_allow_html=True
            )

            st.download_button(
                label="Baixar PDF",
                data=pdf_file,
                file_name=filename,
                mime="application/pdf",
                key=f"download_{orgao_sel}_{subtitulo_sel}_{pdf_id}"
            )

            if user_is_admin and st.button("Excluir PDF", key=f"delete_pdf_main_{pdf_id}"):
                delete_pdf(pdf_id)
                st.session_state.selected_pdf_id = None
                st.session_state.selected_orgao = None
                st.session_state.selected_subtitulo = None
                st.success(f"PDF '{display_title}' excluído!")
                st.rerun()

            if st.button("Analisar com IA", key=f"analyze_{pdf_id}"):
                st.info("Funcionalidade de análise de IA ainda não implementada.")
        else:
            st.error("PDF não encontrado no banco.")

if __name__ == "__main__":
    main()
