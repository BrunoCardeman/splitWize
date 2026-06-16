"""Testes unitários para os casos de uso de usuários."""
from unittest.mock import MagicMock
import pytest

from domain.user import User
from use_cases.user_use_cases import CreateUserUseCase, ListUsersUseCase


class TestCreateUserUseCase:
    """Testes para CreateUserUseCase."""

    def _make_use_case(self, existing_user=None):
        """Helper que cria o use case com repositório mockado."""
        repo = MagicMock()
        repo.find_by_email.return_value = existing_user
        repo.save.side_effect = lambda u: User(id=1, name=u.name, email=u.email)
        return CreateUserUseCase(repo), repo

    def test_create_user_success(self):
        """Deve criar usuário com dados válidos."""
        use_case, repo = self._make_use_case(existing_user=None)
        user = use_case.execute("Ana", "ana@email.com")
        assert user.id == 1
        assert user.name == "Ana"
        assert user.email == "ana@email.com"
        repo.save.assert_called_once()

    def test_create_user_duplicate_email_raises(self):
        """Deve lançar ValueError para e-mail já cadastrado."""
        existing = User(id=1, name="Ana", email="ana@email.com")
        use_case, _ = self._make_use_case(existing_user=existing)
        with pytest.raises(ValueError, match="já está cadastrado"):
            use_case.execute("Outro", "ana@email.com")

    def test_create_user_invalid_email_raises(self):
        """Deve lançar ValueError para e-mail inválido."""
        use_case, _ = self._make_use_case(existing_user=None)
        with pytest.raises(ValueError):
            use_case.execute("Ana", "emailsemarroba")

    def test_create_user_empty_name_raises(self):
        """Deve lançar ValueError para nome vazio."""
        use_case, _ = self._make_use_case(existing_user=None)
        with pytest.raises(ValueError):
            use_case.execute("", "ana@email.com")

    def test_create_user_strips_whitespace(self):
        """Deve remover espaços extras do nome e e-mail."""
        use_case, repo = self._make_use_case(existing_user=None)
        use_case.execute("  Ana  ", "  ANA@EMAIL.COM  ")
        saved_user = repo.save.call_args[0][0]
        assert saved_user.name == "Ana"
        assert saved_user.email == "ana@email.com"


class TestListUsersUseCase:
    """Testes para ListUsersUseCase."""

    def test_list_users_returns_all(self):
        """Deve retornar todos os usuários do repositório."""
        repo = MagicMock()
        repo.find_all.return_value = [
            User(id=1, name="Ana", email="ana@e.com"),
            User(id=2, name="Bob", email="bob@e.com"),
        ]
        result = ListUsersUseCase(repo).execute()
        assert len(result) == 2
        assert result[0].name == "Ana"

    def test_list_users_empty(self):
        """Deve retornar lista vazia se não há usuários."""
        repo = MagicMock()
        repo.find_all.return_value = []
        result = ListUsersUseCase(repo).execute()
        assert result == []