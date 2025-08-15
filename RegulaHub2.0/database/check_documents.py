# regulahub2.0/check_documents.py
import os
from sqlalchemy import create_engine, text

# Pega a URL externa do Render (melhor via variável de ambiente)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:senha@host:porta/nome_do_banco")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, title, orgao, subtema, filename, upload_date, data_publicacao
        FROM documentos
    """))
    documentos = result.fetchall()

print("Documentos na tabela:")
if documentos:
    for doc in documentos:
        print(doc)
else:
    print("Nenhum documento encontrado na tabela 'documentos'.")
