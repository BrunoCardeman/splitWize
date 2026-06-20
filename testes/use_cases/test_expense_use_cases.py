"""Testes unitários para os casos de uso de despesas."""
from unittest.mock import MagicMock
import pytest

from domain.expense import Expense
from domain.user import User
from domain.group import Group
from use_cases.expense_use_cases import (
    CreateExpenseUseCase,
    ListExpensesUseCase,
    SummaryUseCase,
)


def _make_user(user_id: int, name: str = "User") -> User:
    return User(id=user_id, name=name, email=f"{name.lower()}@e.com")


def _make_expense(exp_id, desc, amount, paid_by, group_id=1, participants=None):
    return Expense(
        id=exp_id,
        description=desc,
        amount=amount,
        paid_by_user_id=paid_by,
        group_id=group_id,
        participant_ids=participants or [],
    )


class TestCreateExpenseUseCase:
    """Testes para CreateExpenseUseCase."""

    def _make_use_case(self, payer=None, participants_map=None, group=None):
        expense_repo = MagicMock()
        expense_repo.save.side_effect = lambda e: Expense(
            id=1, description=e.description, amount=e.amount,
            paid_by_user_id=e.paid_by_user_id, group_id=e.group_id,
            participant_ids=e.participant_ids,
        )
        user_repo = MagicMock()
        user_repo.find_by_id.side_effect = lambda uid: (
            participants_map.get(uid) if participants_map else payer if uid == (payer.id if payer else None) else None
        )
        
        group_repo = MagicMock()
        group_obj = group or Group(id=1, name="Praia", created_by_user_id=1)
        group_repo.find_by_id.return_value = group_obj
        group_members = list(participants_map.values()) if participants_map else [payer] if payer else []
        group_repo.get_members.return_value = group_members

        return CreateExpenseUseCase(expense_repo, user_repo, group_repo)

    def test_create_expense_success(self):
        """Deve criar despesa com dados válidos."""
        payer = _make_user(1, "Ana")
        participant = _make_user(2, "Bob")
        users = {1: payer, 2: participant}
        use_case = self._make_use_case(participants_map=users)
        expense = use_case.execute("Jantar", 60.0, 1, 1, [1, 2])
        assert expense.id == 1
        assert expense.amount == 60.0
        assert expense.group_id == 1

    def test_create_expense_invalid_group_raises(self):
        """Deve lançar ValueError se o grupo não existe."""
        expense_repo = MagicMock()
        user_repo = MagicMock()
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = None
        use_case = CreateExpenseUseCase(expense_repo, user_repo, group_repo)
        with pytest.raises(ValueError, match="Grupo com ID"):
            use_case.execute("Jantar", 60.0, 1, 99, [1, 2])

    def test_create_expense_invalid_payer_raises(self):
        """Deve lançar ValueError se pagador não existe."""
        payer = _make_user(1, "Ana")
        participant = _make_user(2, "Bob")
        users = {1: payer, 2: participant}
        
        # Criamos o use_case mas mockamos o user_repo para retornar None para o pagador
        expense_repo = MagicMock()
        user_repo = MagicMock()
        user_repo.find_by_id.return_value = None
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=1)
        
        use_case = CreateExpenseUseCase(expense_repo, user_repo, group_repo)
        with pytest.raises(ValueError, match="pagador"):
            use_case.execute("Jantar", 60.0, 99, 1, [1, 2])

    def test_create_expense_payer_not_in_group_raises(self):
        """Deve lançar ValueError se pagador não pertence ao grupo."""
        payer = _make_user(1, "Ana")
        participant = _make_user(2, "Bob")
        users = {1: payer, 2: participant}
        
        expense_repo = MagicMock()
        user_repo = MagicMock()
        user_repo.find_by_id.side_effect = lambda uid: users.get(uid)
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=2)
        # Pagador (Ana, ID 1) não é membro do grupo (só Bob, ID 2)
        group_repo.get_members.return_value = [participant]

        use_case = CreateExpenseUseCase(expense_repo, user_repo, group_repo)
        with pytest.raises(ValueError, match="não participa do grupo"):
            use_case.execute("Jantar", 60.0, 1, 1, [1, 2])

    def test_create_expense_participant_not_in_group_raises(self):
        """Deve lançar ValueError se algum participante não pertence ao grupo."""
        payer = _make_user(1, "Ana")
        participant = _make_user(2, "Bob")
        users = {1: payer, 2: participant}
        
        expense_repo = MagicMock()
        user_repo = MagicMock()
        user_repo.find_by_id.side_effect = lambda uid: users.get(uid)
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=1)
        # Apenas Ana é membro do grupo, Bob não é
        group_repo.get_members.return_value = [payer]

        use_case = CreateExpenseUseCase(expense_repo, user_repo, group_repo)
        with pytest.raises(ValueError, match="não participa do grupo"):
            use_case.execute("Jantar", 60.0, 1, 1, [1, 2])

    def test_create_expense_negative_amount_raises(self):
        """Deve lançar ValueError para valor negativo."""
        payer = _make_user(1, "Ana")
        use_case = self._make_use_case(participants_map={1: payer})
        with pytest.raises(ValueError):
            use_case.execute("Jantar", -10.0, 1, 1, [1])

    def test_create_expense_no_participants_raises(self):
        """Deve lançar ValueError sem participantes."""
        payer = _make_user(1, "Ana")
        use_case = self._make_use_case(participants_map={1: payer})
        with pytest.raises(ValueError):
            use_case.execute("Jantar", 60.0, 1, 1, [])


class TestSummaryUseCase:
    """Testes para SummaryUseCase."""

    def test_summary_single_expense(self):
        """
        Ana paga R$60 e divide com Bob.
        Bob deve R$30 para Ana.
        """
        expense_repo = MagicMock()
        expense_repo.find_by_group_id.return_value = [
            _make_expense(1, "Jantar", 60.0, paid_by=1, group_id=1, participants=[1, 2])
        ]
        user_repo = MagicMock()
        user_repo.find_by_id.side_effect = lambda uid: {
            1: _make_user(1, "Ana"),
            2: _make_user(2, "Bob"),
        }.get(uid)
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=1)

        debts = SummaryUseCase(expense_repo, user_repo, group_repo).execute(1)
        assert len(debts) == 1
        assert debts[0]["from_name"] == "Bob"
        assert debts[0]["to_name"] == "Ana"
        assert debts[0]["amount"] == 30.0

    def test_summary_no_expenses(self):
        """Sem despesas, sem dívidas."""
        expense_repo = MagicMock()
        expense_repo.find_by_group_id.return_value = []
        user_repo = MagicMock()
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=1)
        debts = SummaryUseCase(expense_repo, user_repo, group_repo).execute(1)
        assert debts == []

    def test_summary_balanced(self):
        """
        Ana paga R$60 (Ana + Bob) e Bob paga R$60 (Ana + Bob).
        Ninguém deve nada.
        """
        expense_repo = MagicMock()
        expense_repo.find_by_group_id.return_value = [
            _make_expense(1, "Jantar", 60.0, paid_by=1, group_id=1, participants=[1, 2]),
            _make_expense(2, "Cinema", 60.0, paid_by=2, group_id=1, participants=[1, 2]),
        ]
        user_repo = MagicMock()
        group_repo = MagicMock()
        group_repo.find_by_id.return_value = Group(id=1, name="Praia", created_by_user_id=1)
        debts = SummaryUseCase(expense_repo, user_repo, group_repo).execute(1)
        assert debts == []