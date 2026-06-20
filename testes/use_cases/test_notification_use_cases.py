"""Testes unitários para casos de uso de notificações."""
from unittest.mock import MagicMock
import pytest

from domain.group import Group
from domain.user import User
from domain.notification import Notification
from use_cases.notification_use_cases import (
    SendReminderUseCase,
    ListNotificationsUseCase,
    MarkNotificationAsReadUseCase,
)


def _make_user(user_id: int, name: str = "User") -> User:
    return User(id=user_id, name=name, email=f"{name.lower()}@e.com")


def _make_group(group_id: int, name: str, creator_id: int) -> Group:
    return Group(id=group_id, name=name, created_by_user_id=creator_id)


class TestSendReminderUseCase:
    """Testes para SendReminderUseCase."""

    def test_send_reminder_success(self):
        """Deve criar e salvar lembrete com sucesso."""
        notification_repo = MagicMock()
        notification_repo.save.side_effect = lambda n: Notification(
            id=1,
            group_id=n.group_id,
            from_user_id=n.from_user_id,
            to_user_id=n.to_user_id,
            message=n.message,
        )

        user_repo = MagicMock()
        users = {1: _make_user(1, "Ana"), 2: _make_user(2, "Bob")}
        user_repo.find_by_id.side_effect = lambda uid: users.get(uid)

        group_repo = MagicMock()
        group_repo.find_by_id.return_value = _make_group(10, "Praia", 1)

        use_case = SendReminderUseCase(notification_repo, user_repo, group_repo)
        notif = use_case.execute(group_id=10, from_user_id=1, to_user_id=2, amount=30.0)

        assert notif.id == 1
        assert notif.group_id == 10
        assert notif.from_user_id == 1
        assert notif.to_user_id == 2
        assert "Ana" in notif.message
        assert "Bob" not in notif.message  # Bob é quem recebe, não quem lembrou
        assert "R$ 30.00" in notif.message
        assert "Praia" in notif.message
        notification_repo.save.assert_called_once()

    def test_send_reminder_invalid_group_raises(self):
        """Deve lançar ValueError se grupo não existe."""
        notification_repo = MagicMock()
        user_repo = MagicMock()
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = None

        use_case = SendReminderUseCase(notification_repo, user_repo, group_repo)
        with pytest.raises(ValueError, match="Grupo com ID"):
            use_case.execute(group_id=99, from_user_id=1, to_user_id=2, amount=30.0)


class TestListNotificationsUseCase:
    """Testes para ListNotificationsUseCase."""

    def test_list_notifications(self):
        """Deve retornar notificações do usuário."""
        notification_repo = MagicMock()
        notification_repo.find_all_for_user.return_value = [
            Notification(group_id=1, from_user_id=1, to_user_id=2, message="Notif 1"),
            Notification(group_id=1, from_user_id=1, to_user_id=2, message="Notif 2"),
        ]

        use_case = ListNotificationsUseCase(notification_repo)
        results = use_case.execute(2)

        assert len(results) == 2
        assert results[0].message == "Notif 1"
        notification_repo.find_all_for_user.assert_called_once_with(2)


class TestMarkNotificationAsReadUseCase:
    """Testes para MarkNotificationAsReadUseCase."""

    def test_mark_as_read(self):
        """Deve chamar repositório para marcar como lida."""
        notification_repo = MagicMock()
        use_case = MarkNotificationAsReadUseCase(notification_repo)
        use_case.execute(5)

        notification_repo.mark_as_read.assert_called_once_with(5)
