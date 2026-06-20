"""Implementação SQLite do repositório de notificações."""
from datetime import datetime
from typing import List

from domain.notification import Notification
from infra.db.database import get_connection
from use_cases.notification_use_cases import AbstractNotificationRepository


class NotificationRepositorySQLite(AbstractNotificationRepository):
    """Repositório concreto de notificações usando SQLite."""

    def save(self, notification: Notification) -> Notification:
        """Salva uma notificação no banco de dados."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO notifications (group_id, from_user_id, to_user_id, message, is_read, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        notification.group_id,
                        notification.from_user_id,
                        notification.to_user_id,
                        notification.message,
                        1 if notification.is_read else 0,
                        notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                notification.id = cursor.lastrowid
            return notification
        finally:
            conn.close()

    def find_all_for_user(self, user_id: int) -> List[Notification]:
        """Busca todas as notificações para um usuário específico (ordenadas por data desc)."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT id, group_id, from_user_id, to_user_id, message, is_read, created_at
                FROM notifications
                WHERE to_user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()

            notifications = []
            for r in rows:
                created_at_dt = datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S")
                notifications.append(
                    Notification(
                        id=r["id"],
                        group_id=r["group_id"],
                        from_user_id=r["from_user_id"],
                        to_user_id=r["to_user_id"],
                        message=r["message"],
                        is_read=True if r["is_read"] == 1 else False,
                        created_at=created_at_dt,
                    )
                )
            return notifications
        finally:
            conn.close()

    def mark_as_read(self, notification_id: int) -> None:
        """Marca uma notificação como lida."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE notifications SET is_read = 1 WHERE id = ?",
                    (notification_id,),
                )
        finally:
            conn.close()

    def count_unread_for_user(self, user_id: int) -> int:
        """Retorna o total de notificações não lidas de um usuário."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) as count FROM notifications WHERE to_user_id = ? AND is_read = 0",
                (user_id,),
            ).fetchone()
            return row["count"] if row else 0
        finally:
            conn.close()
