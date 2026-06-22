"""Casos de uso relacionados a despesas."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from domain.expense import Expense
from use_cases.user_use_cases import AbstractUserRepository
from use_cases.group_use_cases import AbstractGroupRepository


class AbstractExpenseRepository(ABC):
    """Interface (porta) para o repositório de despesas — princípio DIP."""

    @abstractmethod
    def save(self, expense: Expense) -> Expense:
        """Persiste uma despesa e retorna com ID gerado."""

    @abstractmethod
    def find_all(self) -> List[Expense]:
        """Retorna todas as despesas."""

    @abstractmethod
    def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Busca despesa por ID."""

    @abstractmethod
    def find_by_group_id(self, group_id: int) -> List[Expense]:
        """Retorna todas as despesas vinculadas a um grupo."""

    @abstractmethod
    def delete(self, expense_id: int) -> None:
        """Exclui uma despesa pelo ID."""


class CreateExpenseUseCase:
    """HU-02 / HU-06: Registrar uma despesa compartilhada em um grupo."""

    def __init__(
        self,
        expense_repository: AbstractExpenseRepository,
        user_repository: AbstractUserRepository,
        group_repository: AbstractGroupRepository,
    ):
        self._expense_repo = expense_repository
        self._user_repo = user_repository
        self._group_repo = group_repository

    def execute(
        self,
        description: str,
        amount: float,
        paid_by_user_id: int,
        group_id: int,
        participant_ids: List[int],
    ) -> Expense:
        """Valida e registra uma nova despesa no grupo."""
        group = self._group_repo.find_by_id(group_id)
        if not group:
            raise ValueError(f"Grupo com ID {group_id} não encontrado.")

        payer = self._user_repo.find_by_id(paid_by_user_id)
        if not payer:
            raise ValueError(f"Usuário pagador com ID {paid_by_user_id} não encontrado.")

        # Buscar membros do grupo para garantir que todos fazem parte dele
        members = self._group_repo.get_members(group_id)
        member_ids = {m.id for m in members}

        if paid_by_user_id not in member_ids:
            raise ValueError(f"O pagador com ID {paid_by_user_id} não participa do grupo '{group.name}'.")

        for uid in participant_ids:
            if uid not in member_ids:
                raise ValueError(f"O participante com ID {uid} não participa do grupo '{group.name}'.")

        expense = Expense(
            description=description,
            amount=float(amount),
            paid_by_user_id=paid_by_user_id,
            group_id=group_id,
            participant_ids=participant_ids,
        )
        return self._expense_repo.save(expense)


class ListExpensesUseCase:
    """HU-03 / HU-07: Listar todas as despesas de um grupo."""

    def __init__(self, expense_repository: AbstractExpenseRepository):
        self._repo = expense_repository

    def execute(self, group_id: Optional[int] = None) -> List[Expense]:
        """Retorna lista de todas as despesas de um grupo específico, ou todas se None."""
        if group_id is not None:
            return self._repo.find_by_group_id(group_id)
        return self._repo.find_all()


MIN_DEBT_TOLERANCE = 0.001


class SummaryUseCase:
    """HU-04 / HU-08: Calcular resumo de dívidas entre usuários de um grupo."""

    def __init__(
        self,
        expense_repository: AbstractExpenseRepository,
        user_repository: AbstractUserRepository,
        group_repository: AbstractGroupRepository,
    ):
        self._expense_repo = expense_repository
        self._user_repo = user_repository
        self._group_repo = group_repository

    def execute(self, group_id: int) -> List[Dict]:
        """
        Calcula quanto cada pessoa deve a cada outra dentro do grupo.

        Retorna lista de dicts: [{from_name, to_name, amount}]
        """
        group = self._group_repo.find_by_id(group_id)
        if not group:
            raise ValueError(f"Grupo com ID {group_id} não encontrado.")

        expenses = self._expense_repo.find_by_group_id(group_id)
        balances = self._calculate_balances(expenses)
        return self._compute_transfers(balances)

    def _calculate_balances(self, expenses: List[Expense]) -> Dict[int, float]:
        """Calcula o saldo consolidado de cada usuário."""
        balances: Dict[int, float] = {}
        for expense in expenses:
            share = expense.share_per_person()
            payer_id = expense.paid_by_user_id

            # Pagador recebe de volta sua parte dos outros
            balances[payer_id] = balances.get(payer_id, 0.0) + expense.amount

            for uid in expense.participant_ids:
                balances[uid] = balances.get(uid, 0.0) - share
        return balances

    def _compute_transfers(self, balances: Dict[int, float]) -> List[Dict]:
        """Calcula as transferências necessárias a partir dos saldos."""
        debts = []
        debtors = {uid: -bal for uid, bal in balances.items() if bal < -MIN_DEBT_TOLERANCE}
        creditors = {uid: bal for uid, bal in balances.items() if bal > MIN_DEBT_TOLERANCE}

        debtors_list = sorted(debtors.items(), key=lambda x: -x[1])
        creditors_list = sorted(creditors.items(), key=lambda x: -x[1])

        i, j = 0, 0
        while i < len(debtors_list) and j < len(creditors_list):
            debtor_id, debt = debtors_list[i]
            creditor_id, credit = creditors_list[j]

            payment = min(debt, credit)
            if payment > MIN_DEBT_TOLERANCE:
                debtor = self._user_repo.find_by_id(debtor_id)
                creditor = self._user_repo.find_by_id(creditor_id)
                debts.append({
                    "from_name": debtor.name if debtor else str(debtor_id),
                    "to_name": creditor.name if creditor else str(creditor_id),
                    "amount": round(payment, 2),
                })

            debtors_list[i] = (debtor_id, debt - payment)
            creditors_list[j] = (creditor_id, credit - payment)

            if debtors_list[i][1] < MIN_DEBT_TOLERANCE:
                i += 1
            if creditors_list[j][1] < MIN_DEBT_TOLERANCE:
                j += 1

        return debts


class DeleteExpenseUseCase:
    """Caso de uso para excluir uma despesa."""

    def __init__(self, expense_repository: AbstractExpenseRepository):
        self._expense_repo = expense_repository

    def execute(self, expense_id: int) -> None:
        """Exclui a despesa pelo ID."""
        expense = self._expense_repo.find_by_id(expense_id)
        if not expense:
            raise ValueError(f"Despesa com ID {expense_id} não encontrada.")
        self._expense_repo.delete(expense_id)