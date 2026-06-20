"""Implementação SQLite do repositório de usuários."""
from typing import List, Optional

from domain.user import User
from infra.db.database import get_connection
from use_cases.user_use_cases import AbstractUserRepository


class UserRepositorySQLite(AbstractUserRepository):
    """Repositório concreto de usuários usando SQLite."""

    def save(self, user: User) -> User:
        """Insere um usuário e retorna com ID."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (user.name, user.email),
                )
                user.id = cursor.lastrowid
            return user
        finally:
            conn.close()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row:
                return User(id=row["id"], name=row["name"], email=row["email"])
            return None
        finally:
            conn.close()

    def find_all(self) -> List[User]:
        """Retorna todos os usuários."""
        conn = get_connection()
        try:
            rows = conn.execute("SELECT id, name, email FROM users").fetchall()
            return [User(id=r["id"], name=r["name"], email=r["email"]) for r in rows]
        finally:
            conn.close()

    def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por e-mail."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, name, email FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
            if row:
                return User(id=row["id"], name=row["name"], email=row["email"])
            return None
        finally:
            conn.close()