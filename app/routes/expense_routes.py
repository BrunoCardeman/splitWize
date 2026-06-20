"""Rotas Flask para despesas."""
from flask import Blueprint, redirect, render_template, request, url_for

from infra.repositories.expense_repository_sqlite import ExpenseRepositorySQLite
from infra.repositories.user_repository_sqlite import UserRepositorySQLite
from infra.repositories.group_repository_sqlite import GroupRepositorySQLite
from use_cases.expense_use_cases import (
    CreateExpenseUseCase,
    ListExpensesUseCase,
    SummaryUseCase,
)
from use_cases.user_use_cases import ListUsersUseCase
from use_cases.group_use_cases import GetGroupDetailsUseCase, ListAllGroupsUseCase

expense_bp = Blueprint("expenses", __name__)


def _get_expense_repo():
    return ExpenseRepositorySQLite()


def _get_user_repo():
    return UserRepositorySQLite()


def _get_group_repo():
    return GroupRepositorySQLite()


@expense_bp.route("/expenses")
def list_expenses():
    """HU-03: Lista todas as despesas globalmente (para histórico/admin)."""
    expenses = ListExpensesUseCase(_get_expense_repo()).execute()
    users = {u.id: u.name for u in ListUsersUseCase(_get_user_repo()).execute()}
    groups = {g.id: g.name for g in ListAllGroupsUseCase(_get_group_repo()).execute()}
    return render_template("expenses.html", expenses=expenses, users=users, groups=groups)


@expense_bp.route("/groups/<int:group_id>/expenses/new", methods=["GET", "POST"])
def add_expense(group_id: int):
    """HU-02 / HU-06: Formulário para registrar despesa vinculada a um grupo."""
    group_repo = _get_group_repo()
    group = GetGroupDetailsUseCase(group_repo).execute(group_id)
    if not group:
        return "Grupo não encontrado", 404

    user_repo = _get_user_repo()
    # Apenas membros do grupo podem ser selecionados
    users = group_repo.get_members(group_id)
    error = None

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount = request.form.get("amount", "0")
        paid_by = request.form.get("paid_by")
        participants = request.form.getlist("participants")

        try:
            use_case = CreateExpenseUseCase(_get_expense_repo(), user_repo, group_repo)
            use_case.execute(
                description=description,
                amount=float(amount),
                paid_by_user_id=int(paid_by),
                group_id=group_id,
                participant_ids=[int(uid) for uid in participants],
            )
            return redirect(url_for("groups.group_detail", group_id=group_id))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template("add_expense.html", group=group, users=users, error=error)


@expense_bp.route("/summary")
def summary():
    """HU-04: Redireciona para grupos, pois o resumo agora é por grupo."""
    return redirect(url_for("groups.list_groups"))