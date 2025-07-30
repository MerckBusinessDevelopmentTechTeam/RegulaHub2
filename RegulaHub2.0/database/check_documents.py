# regulahub2.0/check_documents.py
import sqlite3

conn = sqlite3.connect("regulahub2.0.db")
c = conn.cursor()
c.execute("SELECT id, title, orgao, subtema, filename, upload_date, data_publicacao FROM documentos")
documentos = c.fetchall()
print("Documentos na tabela:")
if documentos:
    for doc in documentos:
        print(doc)
else:
    print("Nenhum documento encontrado na tabela 'documentos'.")
conn.close()