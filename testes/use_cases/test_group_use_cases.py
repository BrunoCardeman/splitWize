"""Testes unitários para os casos de uso de grupos."""
from unittest.mock import MagicMock
import pytest

from domain.group import Group
from domain.user import User
from use_cases.group_use_cases import (
    CreateGroupUseCase,
    ListUserGroupsUseCase,
    GetGroupDetailsUseCase,
    AddMemberUseCase,
)


def _make_user(user_id: int, name: str = "User") -> User:
    return User(id=user_id, name=name, email=f"{name.lower()}@e.com")


def _make_group(group_id: int, name: str, creator_id: int, members: list = None) -> Group:
    return Group(
        id=group_id,
        name=name,
        created_by_user_id=creator_id,
        member_ids=members or [creator_id],
    )


class TestCreateGroupUseCase:
    """Testes para o caso de uso CreateGroupUseCase."""

    def test_create_group_success(self):
        """Deve criar grupo e associar membros com sucesso."""
        group_repo = MagicMock()
        group_repo.save.side_effect = lambda g: Group(
            id=1, name=g.name, created_by_user_id=g.created_by_user_id
        )
        user_repo = MagicMock()
        # Mocking finding users (creator 1 and members 1, 2)
        users = {1: _make_user(1, "Ana"), 2: _make_user(2, "Bob")}
        user_repo.find_by_id.side_effect = lambda uid: users.get(uid)

        use_case = CreateGroupUseCase(group_repo, user_repo)
        group = use_case.execute("Apartamento", 1, [2])

        assert group.id == 1
        assert group.name == "Apartamento"
        assert 1 in group.member_ids
        assert 2 in group.member_ids
        group_repo.save.assert_called_once()
        assert group_repo.add_member.call_count == 2

    def test_create_group_invalid_creator_raises(self):
        """Deve lançar ValueError se o criador não existe."""
        group_repo = MagicMock()
        user_repo = MagicMock()
        user_repo.find_by_id.return_value = None

        use_case = CreateGroupUseCase(group_repo, user_repo)
        with pytest.raises(ValueError, match="Criador com ID"):
            use_case.execute("Apartamento", 99, [2])

    def test_create_group_invalid_member_raises(self):
        """Deve lançar ValueError se algum participante não existe."""
        group_repo = MagicMock()
        user_repo = MagicMock()
        creator = _make_user(1, "Ana")
        user_repo.find_by_id.side_effect = lambda uid: creator if uid == 1 else None

        use_case = CreateGroupUseCase(group_repo, user_repo)
        with pytest.raises(ValueError, match="Participante com ID"):
            use_case.execute("Apartamento", 1, [99])


class TestListUserGroupsUseCase:
    """Testes para o caso de uso ListUserGroupsUseCase."""

    def test_list_user_groups(self):
        """Deve retornar a lista de grupos em que o usuário participa."""
        group_repo = MagicMock()
        group_repo.find_all_for_user.return_value = [
            _make_group(1, "Praia", 1, [1, 2]),
            _make_group(2, "Viagem", 2, [1, 2]),
        ]
        use_case = ListUserGroupsUseCase(group_repo)
        groups = use_case.execute(1)

        assert len(groups) == 2
        assert groups[0].name == "Praia"
        assert groups[1].name == "Viagem"
        group_repo.find_all_for_user.assert_called_once_with(1)


class TestGetGroupDetailsUseCase:
    """Testes para o caso de uso GetGroupDetailsUseCase."""

    def test_get_group_details_success(self):
        """Deve retornar os detalhes do grupo e preencher IDs dos membros."""
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = _make_group(1, "Apartamento", 1, [])
        group_repo.get_members.return_value = [
            _make_user(1, "Ana"),
            _make_user(2, "Bob"),
        ]

        use_case = GetGroupDetailsUseCase(group_repo)
        group = use_case.execute(1)

        assert group is not None
        assert group.name == "Apartamento"
        assert group.member_ids == [1, 2]
        group_repo.find_by_id.assert_called_once_with(1)
        group_repo.get_members.assert_called_once_with(1)

    def test_get_group_details_not_found(self):
        """Deve retornar None se o grupo não for encontrado."""
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = None

        use_case = GetGroupDetailsUseCase(group_repo)
        group = use_case.execute(99)

        assert group is None


class TestAddMemberUseCase:
    """Testes para o caso de uso AddMemberUseCase."""

    def test_add_member_success(self):
        """Deve adicionar novo membro com sucesso."""
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = _make_group(1, "Apartamento", 1, [1])
        group_repo.get_members.return_value = [_make_user(1, "Ana")]
        user_repo = MagicMock()
        user_repo.find_by_id.return_value = _make_user(2, "Bob")

        use_case = AddMemberUseCase(group_repo, user_repo)
        use_case.execute(1, 2)

        group_repo.add_member.assert_called_once_with(1, 2)

    def test_add_member_already_in_group(self):
        """Não deve tentar adicionar novamente se usuário já for membro."""
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = _make_group(1, "Apartamento", 1, [1, 2])
        group_repo.get_members.return_value = [_make_user(1, "Ana"), _make_user(2, "Bob")]
        user_repo = MagicMock()
        user_repo.find_by_id.return_value = _make_user(2, "Bob")

        use_case = AddMemberUseCase(group_repo, user_repo)
        use_case.execute(1, 2)

        group_repo.add_member.assert_not_called()
