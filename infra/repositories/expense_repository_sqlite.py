"""Implementação SQLite do repositório de despesas."""
from typing import List, Optional

from domain.expense import Expense
from infra.db.database import get_connection
from use_cases.expense_use_cases import AbstractExpenseRepository


class ExpenseRepositorySQLite(AbstractExpenseRepository):
    """Repositório concreto de despesas usando SQLite."""

    def save(self, expense: Expense) -> Expense:
        """Insere uma despesa e seus participantes."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (description, amount, paid_by_user_id) VALUES (?, ?, ?)",
            (expense.description, expense.amount, expense.paid_by_user_id),
        )
        expense.id = cursor.lastrowid

        for uid in expense.participant_ids:
            cursor.execute(
                "INSERT INTO expense_participants (expense_id, user_id) VALUES (?, ?)",
                (expense.id, uid),
            )

        conn.commit()
        conn.close()
        return expense

    def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Busca despesa por ID com seus participantes."""
        conn = get_connection()
        row = conn.execute(
            "SELECT id, description, amount, paid_by_user_id FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        if not row:
            conn.close()
            return None

        participants = conn.execute(
            "SELECT user_id FROM expense_participants WHERE expense_id = ?",
            (expense_id,),
        ).fetchall()
        conn.close()

        return Expense(
            id=row["id"],
            description=row["description"],
            amount=row["amount"],
            paid_by_user_id=row["paid_by_user_id"],
            participant_ids=[p["user_id"] for p in participants],
        )

    def find_all(self) -> List[Expense]:
        """Retorna todas as despesas com participantes."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, description, amount, paid_by_user_id FROM expenses"
        ).fetchall()

        expenses = []
        for row in rows:
            participants = conn.execute(
                "SELECT user_id FROM expense_participants WHERE expense_id = ?",
                (row["id"],),
            ).fetchall()
            expenses.append(Expense(
                id=row["id"],
                description=row["description"],
                amount=row["amount"],
                paid_by_user_id=row["paid_by_user_id"],
                participant_ids=[p["user_id"] for p in participants],
            ))

        conn.close()
        return expenses