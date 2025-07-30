# regulahub2.0/database/db_init.py
import sqlite3
from .user_management import add_user, is_admin

# Dicionários de tópicos e órgãos
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
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    
    # Criação da tabela 'users'
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (name TEXT, email TEXT PRIMARY KEY, password TEXT, is_admin INTEGER DEFAULT 0)''')
    
    # Criação da tabela 'documentos'
    c.execute('''CREATE TABLE IF NOT EXISTS documentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT, filename TEXT, title TEXT, arquivo BLOB, upload_date TEXT,
                  orgao TEXT, subtema TEXT, data_publicacao TEXT,
                  FOREIGN KEY (email) REFERENCES users(email))''')
    
    conn.commit()

    # Verifica se já existe um usuário administrador
    c.execute("SELECT email FROM users WHERE is_admin = 1")
    if not c.fetchone():
        # Cria usuário administrador padrão
        add_user(
            name="Izaque",
            email="izaque.lopes@merckgroup.com",
            password="Pizza.10",
            is_admin=1
        )

    conn.close()