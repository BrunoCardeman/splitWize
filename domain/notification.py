"""Entidade de domínio: Notification."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    """Representa um lembrete/notificação de pagamento no sistema."""

    group_id: int
    from_user_id: int
    to_user_id: int
    message: str
    is_read: bool = False
    id: int = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.group_id:
            raise ValueError("O grupo da notificação deve ser especificado.")
        if not self.from_user_id:
            raise ValueError("O remetente da notificação deve ser especificado.")
        if not self.to_user_id:
            raise ValueError("O destinatário da notificação deve ser especificado.")
        if not self.message or not self.message.strip():
            raise ValueError("A mensagem da notificação não pode ser vazia.")
