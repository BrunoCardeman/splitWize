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
    try:
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT    NOT NULL,
                    email TEXT    NOT NULL UNIQUE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                    name               TEXT    NOT NULL,
                    created_by_user_id INTEGER NOT NULL,
                    created_at         TEXT    NOT NULL,
                    FOREIGN KEY (created_by_user_id) REFERENCES users(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    group_id INTEGER NOT NULL,
                    user_id  INTEGER NOT NULL,
                    PRIMARY KEY (group_id, user_id),
                    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id)  REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    description     TEXT    NOT NULL,
                    amount          REAL    NOT NULL,
                    paid_by_user_id INTEGER NOT NULL,
                    group_id        INTEGER NOT NULL,
                    created_at      TEXT    NOT NULL,
                    FOREIGN KEY (paid_by_user_id) REFERENCES users(id),
                    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expense_participants (
                    expense_id INTEGER NOT NULL,
                    user_id    INTEGER NOT NULL,
                    PRIMARY KEY (expense_id, user_id),
                    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id     INTEGER NOT NULL,
                    from_user_id INTEGER NOT NULL,
                    to_user_id   INTEGER NOT NULL,
                    message      TEXT    NOT NULL,
                    is_read      INTEGER NOT NULL DEFAULT 0,
                    created_at   TEXT    NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
    finally:
        conn.close()