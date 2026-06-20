"""Implementação SQLite do repositório de grupos."""
from datetime import datetime
from typing import List, Optional

from domain.group import Group
from domain.user import User
from infra.db.database import get_connection
from use_cases.group_use_cases import AbstractGroupRepository


class GroupRepositorySQLite(AbstractGroupRepository):
    """Repositório concreto de grupos usando SQLite."""

    def save(self, group: Group) -> Group:
        """Salva um grupo no banco de dados."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO groups (name, created_by_user_id, created_at) VALUES (?, ?, ?)",
                    (
                        group.name,
                        group.created_by_user_id,
                        group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                group.id = cursor.lastrowid
            return group
        finally:
            conn.close()

    def find_by_id(self, group_id: int) -> Optional[Group]:
        """Busca um grupo por ID."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, name, created_by_user_id, created_at FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()
            if not row:
                return None

            members_rows = conn.execute(
                "SELECT user_id FROM group_members WHERE group_id = ?", (group_id,)
            ).fetchall()

            created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
            return Group(
                id=row["id"],
                name=row["name"],
                created_by_user_id=row["created_by_user_id"],
                created_at=created_at_dt,
                member_ids=[r["user_id"] for r in members_rows],
            )
        finally:
            conn.close()

    def find_all(self) -> List[Group]:
        """Retorna todos os grupos do sistema."""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name, created_by_user_id, created_at FROM groups"
            ).fetchall()

            groups = []
            for row in rows:
                members_rows = conn.execute(
                    "SELECT user_id FROM group_members WHERE group_id = ?", (row["id"],)
                ).fetchall()
                created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
                groups.append(
                    Group(
                        id=row["id"],
                        name=row["name"],
                        created_by_user_id=row["created_by_user_id"],
                        created_at=created_at_dt,
                        member_ids=[r["user_id"] for r in members_rows],
                    )
                )
            return groups
        finally:
            conn.close()

    def find_all_for_user(self, user_id: int) -> List[Group]:
        """Retorna todos os grupos de que um usuário participa."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT g.id, g.name, g.created_by_user_id, g.created_at
                FROM groups g
                JOIN group_members gm ON g.id = gm.group_id
                WHERE gm.user_id = ?
                """,
                (user_id,),
            ).fetchall()

            groups = []
            for row in rows:
                members_rows = conn.execute(
                    "SELECT user_id FROM group_members WHERE group_id = ?", (row["id"],)
                ).fetchall()
                created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
                groups.append(
                    Group(
                        id=row["id"],
                        name=row["name"],
                        created_by_user_id=row["created_by_user_id"],
                        created_at=created_at_dt,
                        member_ids=[r["user_id"] for r in members_rows],
                    )
                )
            return groups
        finally:
            conn.close()

    def add_member(self, group_id: int, user_id: int) -> None:
        """Adiciona um membro a um grupo."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)",
                    (group_id, user_id),
                )
        finally:
            conn.close()

    def get_members(self, group_id: int) -> List[User]:
        """Retorna todos os usuários membros do grupo."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT u.id, u.name, u.email
                FROM users u
                JOIN group_members gm ON u.id = gm.user_id
                WHERE gm.group_id = ?
                """,
                (group_id,),
            ).fetchall()
            return [User(id=r["id"], name=r["name"], email=r["email"]) for r in rows]
        finally:
            conn.close()
