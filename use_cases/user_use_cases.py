"""Casos de uso relacionados a usuários."""
from abc import ABC, abstractmethod
from typing import List, Optional

from domain.user import User


class AbstractUserRepository(ABC):
    """Interface (porta) para o repositório de usuários — princípio DIP."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persiste um usuário e retorna com ID gerado."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID."""

    @abstractmethod
    def find_all(self) -> List[User]:
        """Retorna todos os usuários."""

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por e-mail."""


class CreateUserUseCase:
    """HU-01: Cadastrar um novo usuário."""

    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self, name: str, email: str) -> User:
        """Cria e persiste um novo usuário."""
        existing = self._repo.find_by_email(email)
        if existing:
            raise ValueError(f"E-mail '{email}' já está cadastrado.")
        user = User(name=name.strip(), email=email.strip().lower())
        return self._repo.save(user)


class ListUsersUseCase:
    """Lista todos os usuários cadastrados."""

    def __init__(self, user_repository: AbstractUserRepository):
        self._repo = user_repository

    def execute(self) -> List[User]:
        """Retorna lista de todos os usuários."""
        return self._repo.find_all()