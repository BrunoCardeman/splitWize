"""Configuração e inicialização do banco de dados SQLite."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "splitfacil.db")


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Cria as tabelas caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            email TEXT    NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            description     TEXT    NOT NULL,
            amount          REAL    NOT NULL,
            paid_by_user_id INTEGER NOT NULL,
            FOREIGN KEY (paid_by_user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_participants (
            expense_id INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            PRIMARY KEY (expense_id, user_id),
            FOREIGN KEY (expense_id) REFERENCES expenses(id),
            FOREIGN KEY (user_id)    REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()