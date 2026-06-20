"""Entidade de domínio: Group."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Group:
    """Representa um grupo de despesas compartilhadas."""

    name: str
    created_by_user_id: int
    id: int = None
    created_at: datetime = field(default_factory=datetime.now)
    member_ids: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nome do grupo não pode ser vazio.")
        if not self.created_by_user_id:
            raise ValueError("O criador do grupo deve ser especificado.")
