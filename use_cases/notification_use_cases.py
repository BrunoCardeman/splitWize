"""Casos de uso relacionados a notificações/lembretes de pagamento."""
from abc import ABC, abstractmethod
from typing import List

from domain.notification import Notification
from use_cases.group_use_cases import AbstractGroupRepository
from use_cases.user_use_cases import AbstractUserRepository


class AbstractNotificationRepository(ABC):
    """Interface para o repositório de notificações — DIP."""

    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        """Salva a notificação."""

    @abstractmethod
    def find_all_for_user(self, user_id: int) -> List[Notification]:
        """Busca todas as notificações para um usuário."""

    @abstractmethod
    def mark_as_read(self, notification_id: int) -> None:
        """Marca notificação como lida."""

    @abstractmethod
    def count_unread_for_user(self, user_id: int) -> int:
        """Retorna o número de notificações não lidas de um usuário."""


class SendReminderUseCase:
    """HU-10: Enviar lembrete de pagamento."""

    def __init__(
        self,
        notification_repo: AbstractNotificationRepository,
        user_repo: AbstractUserRepository,
        group_repo: AbstractGroupRepository,
    ):
        self._notification_repo = notification_repo
        self._user_repo = user_repo
        self._group_repo = group_repo

    def execute(self, group_id: int, from_user_id: int, to_user_id: int, amount: float) -> Notification:
        """Cria e salva um lembrete de pagamento no sistema."""
        group = self._group_repo.find_by_id(group_id)
        if not group:
            raise ValueError(f"Grupo com ID {group_id} não encontrado.")

        sender = self._user_repo.find_by_id(from_user_id)
        if not sender:
            raise ValueError(f"Remetente com ID {from_user_id} não encontrado.")

        receiver = self._user_repo.find_by_id(to_user_id)
        if not receiver:
            raise ValueError(f"Destinatário com ID {to_user_id} não encontrado.")

        message = f"{sender.name} lembrou que você deve R$ {amount:.2f} no grupo '{group.name}'."
        notification = Notification(
            group_id=group_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message=message,
        )
        return self._notification_repo.save(notification)


class ListNotificationsUseCase:
    """HU-11: Listar notificações de um usuário."""

    def __init__(self, notification_repo: AbstractNotificationRepository):
        self._notification_repo = notification_repo

    def execute(self, user_id: int) -> List[Notification]:
        """Retorna todas as notificações do usuário."""
        return self._notification_repo.find_all_for_user(user_id)


class MarkNotificationAsReadUseCase:
    """Marcar notificação como lida."""

    def __init__(self, notification_repo: AbstractNotificationRepository):
        self._notification_repo = notification_repo

    def execute(self, notification_id: int) -> None:
        """Executa a ação no repositório."""
        self._notification_repo.mark_as_read(notification_id)
