"""Implementação SQLite do repositório de despesas."""
from datetime import datetime
from typing import List, Optional

from domain.expense import Expense
from infra.db.database import get_connection
from use_cases.expense_use_cases import AbstractExpenseRepository


class ExpenseRepositorySQLite(AbstractExpenseRepository):
    """Repositório concreto de despesas usando SQLite."""

    def save(self, expense: Expense) -> Expense:
        """Insere uma despesa e seus participantes."""
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses (description, amount, paid_by_user_id, group_id, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        expense.description,
                        expense.amount,
                        expense.paid_by_user_id,
                        expense.group_id,
                        expense.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                expense.id = cursor.lastrowid

                for uid in expense.participant_ids:
                    cursor.execute(
                        "INSERT INTO expense_participants (expense_id, user_id) VALUES (?, ?)",
                        (expense.id, uid),
                    )
            return expense
        finally:
            conn.close()

    def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Busca despesa por ID com seus participantes."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, description, amount, paid_by_user_id, group_id, created_at FROM expenses WHERE id = ?",
                (expense_id,),
            ).fetchone()
            if not row:
                return None

            participants = conn.execute(
                "SELECT user_id FROM expense_participants WHERE expense_id = ?",
                (expense_id,),
            ).fetchall()

            created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
            return Expense(
                id=row["id"],
                description=row["description"],
                amount=row["amount"],
                paid_by_user_id=row["paid_by_user_id"],
                group_id=row["group_id"],
                participant_ids=[p["user_id"] for p in participants],
                created_at=created_at_dt,
            )
        finally:
            conn.close()

    def find_all(self) -> List[Expense]:
        """Retorna todas as despesas com participantes usando JOIN para evitar query N+1."""
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT e.id, e.description, e.amount, e.paid_by_user_id, e.group_id, e.created_at, ep.user_id
                FROM expenses e
                LEFT JOIN expense_participants ep ON e.id = ep.expense_id
            """).fetchall()

            expenses_dict = {}
            for row in rows:
                exp_id = row["id"]
                if exp_id not in expenses_dict:
                    created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
                    expenses_dict[exp_id] = {
                        "id": exp_id,
                        "description": row["description"],
                        "amount": row["amount"],
                        "paid_by_user_id": row["paid_by_user_id"],
                        "group_id": row["group_id"],
                        "created_at": created_at_dt,
                        "participant_ids": []
                    }
                if row["user_id"] is not None:
                    expenses_dict[exp_id]["participant_ids"].append(row["user_id"])

            return [
                Expense(
                    id=data["id"],
                    description=data["description"],
                    amount=data["amount"],
                    paid_by_user_id=data["paid_by_user_id"],
                    group_id=data["group_id"],
                    participant_ids=data["participant_ids"],
                    created_at=data["created_at"]
                )
                for data in expenses_dict.values()
            ]
        finally:
            conn.close()

    def find_by_group_id(self, group_id: int) -> List[Expense]:
        """Retorna todas as despesas vinculadas a um grupo específico ordenadas por data desc."""
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT e.id, e.description, e.amount, e.paid_by_user_id, e.group_id, e.created_at, ep.user_id
                FROM expenses e
                LEFT JOIN expense_participants ep ON e.id = ep.expense_id
                WHERE e.group_id = ?
                ORDER BY e.created_at DESC, e.id DESC
            """, (group_id,)).fetchall()

            expenses_dict = {}
            for row in rows:
                exp_id = row["id"]
                if exp_id not in expenses_dict:
                    created_at_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
                    expenses_dict[exp_id] = {
                        "id": exp_id,
                        "description": row["description"],
                        "amount": row["amount"],
                        "paid_by_user_id": row["paid_by_user_id"],
                        "group_id": row["group_id"],
                        "created_at": created_at_dt,
                        "participant_ids": []
                    }
                if row["user_id"] is not None:
                    expenses_dict[exp_id]["participant_ids"].append(row["user_id"])

            return [
                Expense(
                    id=data["id"],
                    description=data["description"],
                    amount=data["amount"],
                    paid_by_user_id=data["paid_by_user_id"],
                    group_id=data["group_id"],
                    participant_ids=data["participant_ids"],
                    created_at=data["created_at"]
                )
                for data in expenses_dict.values()
            ]
        finally:
            conn.close()