"""Entidade de domínio: User."""
from dataclasses import dataclass


@dataclass
class User:
    """Representa um usuário do sistema."""

    name: str
    email: str
    id: int = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nome do usuário não pode ser vazio.")
        if "@" not in self.email:
            raise ValueError("E-mail inválido.")