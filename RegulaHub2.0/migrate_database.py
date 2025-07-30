# regulahub2.0/database/migrate_database.py
import sqlite3

def migrate_database():
    db_path = "regulahub2.0.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Verifica as colunas existentes na tabela 'documentos'
    c.execute("PRAGMA table_info(documentos)")
    existing_columns = [col[1] for col in c.fetchall()]

    # Nome e tipo da nova coluna
    new_column = "data_publicacao"
    column_type = "TEXT"

    # Adiciona a nova coluna se ela não existir
    if new_column not in existing_columns:
        print(f"Adicionando coluna '{new_column}' à tabela 'documentos'...")
        c.execute(f"ALTER TABLE documentos ADD COLUMN {new_column} {column_type}")
        print(f"Coluna '{new_column}' adicionada com sucesso.")
    else:
        print(f"A coluna '{new_column}' já existe na tabela 'documentos'.")

    # Confirma as alterações
    conn.commit()

    # Verifica a estrutura final da tabela
    c.execute("PRAGMA table_info(documentos)")
    columns = c.fetchall()
    print("Estrutura atual da tabela 'documentos':")
    for col in columns:
        print(f"Coluna: {col[1]}, Tipo: {col[2]}")

    # Fecha a conexão
    conn.close()
    print(f"Migração concluída. Banco de dados {db_path} atualizado.")

if __name__ == "__main__":
    migrate_database()