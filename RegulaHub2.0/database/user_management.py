# regulahub2.0/database/user_management.py

import os
import bcrypt
import streamlit as st
from sqlalchemy import create_engine, text

# =========================
# Configuração do Banco de Dados PostgreSQL
# =========================
# Pega do ambiente ou usa valor padrão
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://regulahub2_0_db_user:scCy9G4gM9H7ifXD8y2kXrUNvTAIdnSJ"
    "@dpg-d29kvqili9vc73fs2vg0-a.ohio-postgres.render.com:5432/regulahub2_0_db"
)

engine = create_engine(DATABASE_URL)

# =========================
# Funções auxiliares de segurança
# =========================
def hash_password(password: str) -> bytes:
    """Gera o hash da senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# =========================
# CRUD de Usuário
# =========================
def add_user(name: str, email: str, password: str, is_admin: int = 0) -> bool:
    """Adiciona novo usuário."""
    if len(password) < 6:
        st.error("A senha deve ter pelo menos 6 caracteres.")
        return False

    hashed = hash_password(password)

    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO users (name, email, password, is_admin)
                    VALUES (:name, :email, :password, :is_admin)
                """),
                {"name": name, "email": email, "password": hashed, "is_admin": is_admin}
            )
        st.success(f"Usuário {email} criado com sucesso!")
        return True
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique constraint" in str(e).lower():
            st.error("E-mail já registrado.")
        else:
            st.error(f"Erro ao criar usuário: {e}")
        return False

def remove_user(email: str):
    """Remove usuário e seus documentos."""
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM documentos WHERE email = :email"), {"email": email})
        conn.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
    st.success(f"Usuário {email} removido com sucesso!")

def get_users():
    """Lista de usuários."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email, is_admin FROM users"))
        return result.fetchall()

def is_admin(email: str) -> bool:
    """Verifica se usuário é admin."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT is_admin FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()
    return result and result[0] == 1

def check_login(email: str, password: str):
    """Verifica credenciais do login."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT name, password FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

    if result:
        name, hashed_password = result

        # 🔹 Converte memoryview -> bytes se necessário (erro original corrigido)
        if isinstance(hashed_password, memoryview):
            hashed_password = hashed_password.tobytes()

        if check_password(password, hashed_password):
            return name

    return None
