# regulahub2.0/database/user_management.py
import sqlite3
import bcrypt
import streamlit as st

def hash_password(password):
    """Hasheia a senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def add_user(name, email, password, is_admin=0):
    """Adiciona um novo usuário ao banco de dados."""
    if len(password) < 6:
        st.error("A senha deve ter pelo menos 6 caracteres.")
        return False
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    hashed = hash_password(password)
    try:
        c.execute("INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)",
                  (name, email, hashed, is_admin))
        conn.commit()
        st.success(f"Usuário {email} criado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        st.error("E-mail já registrado.")
        return False
    finally:
        conn.close()

def remove_user(email):
    """Remove um usuário e seus documentos do banco de dados."""
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    c.execute("DELETE FROM documentos WHERE email = ?", (email,))
    c.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    st.success(f"Usuário {email} removido com sucesso!")

def get_users():
    """Retorna a lista de usuários."""
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    c.execute("SELECT email, is_admin FROM users")
    users = c.fetchall()
    conn.close()
    return users

def is_admin(email):
    """Verifica se o usuário é administrador."""
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] == 1 if result else False

def check_login(email, password):
    """Verifica as credenciais de login."""
    conn = sqlite3.connect("regulahub2.0.db")
    c = conn.cursor()
    c.execute("SELECT name, password FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    if result:
        name, hashed_password = result
        if check_password(password, hashed_password):
            return name
    return None