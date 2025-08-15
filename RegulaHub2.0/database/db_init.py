# regulahub2.0/database/db_init.py

import os
from sqlalchemy import create_engine, text
from .user_management import add_user

# URL de conexão PostgreSQL do Render (recomendo usar variável de ambiente)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://regulahub2_0_db_user:scCy9G4gM9H7ifXD8y2kXrUNvTAIdnSJ@dpg-d29kvqili9vc73fs2vg0-a.ohio-postgres.render.com:5432/regulahub2_0_db")

engine = create_engine(DATABASE_URL)

# Dicionários mantidos normalmente
TOPICS = {
    "Regulamentações": [
        "Normas Técnicas", "Compliance", "Auditoria",
        "Licenciamento", "Certificações", "Legislação"
    ],
    "Relatórios Técnicos": [
        "Análise de Dados", "Testes Laboratoriais", "Resultados Experimentais",
        "Relatórios de Campo", "Estudos de Caso", "Documentação Interna"
    ],
    "Projetos": [
        "Planejamento", "Execução", "Monitoramento",
        "Avaliação", "Propostas", "Relatórios Finais"
    ],
    "Pesquisas": [
        "Artigos Científicos", "Revisões Bibliográficas", "Patentes",
        "Estudos de Mercado", "Relatórios de Pesquisa", "White Papers"
    ],
    "Treinamentos": [
        "Manuais", "Guias de Procedimento", "Materiais Didáticos",
        "Avaliações", "Certificados", "Apresentações"
    ],
    "Administração": [
        "Contratos", "Orçamentos", "Correspondências",
        "Relatórios Financeiros", "Políticas Internas"
    ]
}

ORGAOS_TITULOS = {
    "ABNT": [],
    "ANAC": [],
    "ANA": [],
    "ANM": [],
    "ANP": [],
    "ANVISA": [
        "Agrotóxicos",
        "Alimentos",
        "Cosméticos",
        "Farmacopeia",
        "Insumos Farmacêuticos",
        "Laboratórios Analíticos",
        "Medicamentos",
        "Produtos Para Saúde",
        "Saneantes",
        "Sangue, Tecidos e Órgãos",
        "Serviços de Interesse para Saúde",
        "Tabaco"
    ],
    "CETESB": [],
    "COVISA (Estado)": [],
    "MAPA": [],
    "MINISTÉRIO DA SAÚDE": [],
    "POLÍCIA FEDERAL": [],
    "RECEITA FEDERAL": []
}

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias no PostgreSQL do Render."""

    with engine.begin() as conn:
        # Criação da tabela users (ajustada para PostgreSQL)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password BYTEA NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        """))

        # Criação da tabela documentos (ajustada para PostgreSQL)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS documentos (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                filename TEXT,
                title TEXT NOT NULL,
                arquivo BYTEA NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                orgao TEXT,
                subtema TEXT,
                data_publicacao TEXT,
                CONSTRAINT fk_user_email FOREIGN KEY(email) REFERENCES users(email) ON DELETE CASCADE
            )
        """))

        # Verifica se já existe um usuário administrador
        result = conn.execute(text("SELECT email FROM users WHERE is_admin = 1"))
        if not result.fetchone():
            # Cria usuário administrador padrão
            add_user(
                name="Izaque",
                email="izaque.lopes@merckgroup.com",
                password="Pizza.10",
                is_admin=1
            )
