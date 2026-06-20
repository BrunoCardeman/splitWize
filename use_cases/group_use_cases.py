"""Casos de uso relacionados a grupos."""
from abc import ABC, abstractmethod
from typing import List, Optional

from domain.group import Group
from domain.user import User
from use_cases.user_use_cases import AbstractUserRepository


class AbstractGroupRepository(ABC):
    """Interface (porta) para o repositório de grupos — DIP."""

    @abstractmethod
    def save(self, group: Group) -> Group:
        """Persiste um grupo e retorna com ID gerado."""

    @abstractmethod
    def find_all(self) -> List[Group]:
        """Retorna todos os grupos do sistema."""

    @abstractmethod
    def find_by_id(self, group_id: int) -> Optional[Group]:
        """Busca um grupo por ID."""

    @abstractmethod
    def find_all_for_user(self, user_id: int) -> List[Group]:
        """Retorna todos os grupos de um determinado usuário."""

    @abstractmethod
    def add_member(self, group_id: int, user_id: int) -> None:
        """Adiciona um participante ao grupo."""

    @abstractmethod
    def get_members(self, group_id: int) -> List[User]:
        """Retorna todos os membros/usuários de um grupo."""


class ListAllGroupsUseCase:
    """Listar todos os grupos cadastrados."""

    def __init__(self, group_repository: AbstractGroupRepository):
        self._group_repo = group_repository

    def execute(self) -> List[Group]:
        """Retorna lista de todos os grupos."""
        return self._group_repo.find_all()


class CreateGroupUseCase:
    """HU-03: Criar um grupo e associar participantes."""

    def __init__(
        self,
        group_repository: AbstractGroupRepository,
        user_repository: AbstractUserRepository,
    ):
        self._group_repo = group_repository
        self._user_repo = user_repository

    def execute(self, name: str, created_by_user_id: int, member_ids: List[int]) -> Group:
        """Valida e cria um novo grupo, associando membros."""
        creator = self._user_repo.find_by_id(created_by_user_id)
        if not creator:
            raise ValueError(f"Criador com ID {created_by_user_id} não encontrado.")

        group = Group(name=name.strip(), created_by_user_id=created_by_user_id)
        saved_group = self._group_repo.save(group)

        # Garantir que o criador faz parte do grupo
        all_member_ids = list(set([created_by_user_id] + member_ids))
        for uid in all_member_ids:
            member = self._user_repo.find_by_id(uid)
            if not member:
                raise ValueError(f"Participante com ID {uid} não encontrado.")
            self._group_repo.add_member(saved_group.id, uid)
            saved_group.member_ids.append(uid)

        return saved_group


class ListUserGroupsUseCase:
    """HU-04: Listar os grupos nos quais o usuário participa."""

    def __init__(self, group_repository: AbstractGroupRepository):
        self._group_repo = group_repository

    def execute(self, user_id: int) -> List[Group]:
        """Retorna todos os grupos de um usuário."""
        return self._group_repo.find_all_for_user(user_id)


class GetGroupDetailsUseCase:
    """HU-05: Buscar detalhes do grupo e seus participantes."""

    def __init__(self, group_repository: AbstractGroupRepository):
        self._group_repo = group_repository

    def execute(self, group_id: int) -> Optional[Group]:
        """Retorna o grupo com membros e detalhes."""
        group = self._group_repo.find_by_id(group_id)
        if not group:
            return None
        members = self._group_repo.get_members(group_id)
        group.member_ids = [m.id for m in members]
        return group


class AddMemberUseCase:
    """Adicionar participante a um grupo existente."""

    def __init__(
        self,
        group_repository: AbstractGroupRepository,
        user_repository: AbstractUserRepository,
    ):
        self._group_repo = group_repository
        self._user_repo = user_repository

    def execute(self, group_id: int, user_id: int) -> None:
        """Adiciona membro ao grupo após validação."""
        group = self._group_repo.find_by_id(group_id)
        if not group:
            raise ValueError(f"Grupo com ID {group_id} não encontrado.")
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Usuário com ID {user_id} não encontrado.")

        # Verificar se já é membro
        members = self._group_repo.get_members(group_id)
        if any(m.id == user_id for m in members):
            return

        self._group_repo.add_member(group_id, user_id)
