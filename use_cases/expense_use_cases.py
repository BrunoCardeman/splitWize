"""Casos de uso relacionados a despesas."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from domain.expense import Expense
from use_cases.user_use_cases import AbstractUserRepository


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


class CreateExpenseUseCase:
    """HU-02: Registrar uma despesa compartilhada."""

    def __init__(
        self,
        expense_repository: AbstractExpenseRepository,
        user_repository: AbstractUserRepository,
    ):
        self._expense_repo = expense_repository
        self._user_repo = user_repository

    def execute(
        self,
        description: str,
        amount: float,
        paid_by_user_id: int,
        participant_ids: List[int],
    ) -> Expense:
        """Valida e registra uma nova despesa."""
        payer = self._user_repo.find_by_id(paid_by_user_id)
        if not payer:
            raise ValueError(f"Usuário pagador com ID {paid_by_user_id} não encontrado.")

        for uid in participant_ids:
            if not self._user_repo.find_by_id(uid):
                raise ValueError(f"Participante com ID {uid} não encontrado.")

        expense = Expense(
            description=description,
            amount=float(amount),
            paid_by_user_id=paid_by_user_id,
            participant_ids=participant_ids,
        )
        return self._expense_repo.save(expense)


class ListExpensesUseCase:
    """HU-03: Listar todas as despesas."""

    def __init__(self, expense_repository: AbstractExpenseRepository):
        self._repo = expense_repository

    def execute(self) -> List[Expense]:
        """Retorna lista de todas as despesas."""
        return self._repo.find_all()


class SummaryUseCase:
    """HU-04: Calcular resumo de dívidas entre usuários."""

    def __init__(
        self,
        expense_repository: AbstractExpenseRepository,
        user_repository: AbstractUserRepository,
    ):
        self._expense_repo = expense_repository
        self._user_repo = user_repository

    def execute(self) -> List[Dict]:
        """
        Calcula quanto cada pessoa deve a cada outra.

        Retorna lista de dicts: [{from_name, to_name, amount}]
        """
        expenses = self._expense_repo.find_all()
        # balance[user_id] = saldo (positivo = a receber, negativo = a pagar)
        balance: Dict[int, float] = {}

        for expense in expenses:
            share = expense.share_per_person()
            payer_id = expense.paid_by_user_id

            # Pagador recebe de volta sua parte dos outros
            balance[payer_id] = balance.get(payer_id, 0) + expense.amount

            for uid in expense.participant_ids:
                balance[uid] = balance.get(uid, 0) - share

        # Converte saldos para lista de transferências simplificadas
        debts = []
        debtors = {uid: -bal for uid, bal in balance.items() if bal < -0.001}
        creditors = {uid: bal for uid, bal in balance.items() if bal > 0.001}

        debtors_list = sorted(debtors.items(), key=lambda x: -x[1])
        creditors_list = sorted(creditors.items(), key=lambda x: -x[1])

        i, j = 0, 0
        while i < len(debtors_list) and j < len(creditors_list):
            debtor_id, debt = debtors_list[i]
            creditor_id, credit = creditors_list[j]

            payment = min(debt, credit)
            if payment > 0.001:
                debtor = self._user_repo.find_by_id(debtor_id)
                creditor = self._user_repo.find_by_id(creditor_id)
                debts.append({
                    "from_name": debtor.name if debtor else str(debtor_id),
                    "to_name": creditor.name if creditor else str(creditor_id),
                    "amount": round(payment, 2),
                })

            debtors_list[i] = (debtor_id, debt - payment)
            creditors_list[j] = (creditor_id, credit - payment)

            if debtors_list[i][1] < 0.001:
                i += 1
            if creditors_list[j][1] < 0.001:
                j += 1

        return debts