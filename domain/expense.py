"""Entidade de domínio: Expense."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Expense:
    """Representa uma despesa compartilhada."""

    description: str
    amount: float
    paid_by_user_id: int
    participant_ids: List[int] = field(default_factory=list)
    id: int = None

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise ValueError("Descrição da despesa não pode ser vazia.")
        if self.amount <= 0:
            raise ValueError("O valor da despesa deve ser positivo.")
        if not self.participant_ids:
            raise ValueError("A despesa precisa ter ao menos um participante.")

    def share_per_person(self) -> float:
        """Calcula a parte de cada participante."""
        return self.amount / len(self.participant_ids)