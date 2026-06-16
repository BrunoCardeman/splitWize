"""Rotas Flask para despesas."""
from flask import Blueprint, redirect, render_template, request, url_for

from infra.repositories.expense_repository_sqlite import ExpenseRepositorySQLite
from infra.repositories.user_repository_sqlite import UserRepositorySQLite
from use_cases.expense_use_cases import (
    CreateExpenseUseCase,
    ListExpensesUseCase,
    SummaryUseCase,
)
from use_cases.user_use_cases import ListUsersUseCase

expense_bp = Blueprint("expenses", __name__)


def _get_expense_repo():
    return ExpenseRepositorySQLite()


def _get_user_repo():
    return UserRepositorySQLite()


@expense_bp.route("/expenses")
def list_expenses():
    """HU-03: Lista todas as despesas."""
    expenses = ListExpensesUseCase(_get_expense_repo()).execute()
    users = {u.id: u.name for u in ListUsersUseCase(_get_user_repo()).execute()}
    return render_template("expenses.html", expenses=expenses, users=users)


@expense_bp.route("/expenses/new", methods=["GET", "POST"])
def add_expense():
    """HU-02: Formulário para registrar despesa."""
    user_repo = _get_user_repo()
    users = ListUsersUseCase(user_repo).execute()
    error = None

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount = request.form.get("amount", "0")
        paid_by = request.form.get("paid_by")
        participants = request.form.getlist("participants")

        try:
            use_case = CreateExpenseUseCase(_get_expense_repo(), user_repo)
            use_case.execute(
                description=description,
                amount=float(amount),
                paid_by_user_id=int(paid_by),
                participant_ids=[int(uid) for uid in participants],
            )
            return redirect(url_for("expenses.list_expenses"))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template("add_expense.html", users=users, error=error)


@expense_bp.route("/summary")
def summary():
    """HU-04: Resumo de dívidas."""
    use_case = SummaryUseCase(_get_expense_repo(), _get_user_repo())
    debts = use_case.execute()
    return render_template("summary.html", debts=debts)