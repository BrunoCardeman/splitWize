"""Rotas Flask para grupos."""
from flask import Blueprint, redirect, render_template, request, url_for, session

from infra.repositories.group_repository_sqlite import GroupRepositorySQLite
from infra.repositories.user_repository_sqlite import UserRepositorySQLite
from use_cases.group_use_cases import (
    CreateGroupUseCase,
    ListAllGroupsUseCase,
    GetGroupDetailsUseCase,
)
from use_cases.user_use_cases import ListUsersUseCase
from use_cases.expense_use_cases import SummaryUseCase, ListExpensesUseCase

group_bp = Blueprint("groups", __name__)


def _get_group_repo():
    return GroupRepositorySQLite()


def _get_user_repo():
    return UserRepositorySQLite()


@group_bp.route("/groups")
def list_groups():
    """HU-04: Exibe lista de todos os grupos."""
    # Listar todos os grupos do sistema
    groups = ListAllGroupsUseCase(_get_group_repo()).execute()
    
    # Listar todos os usuários para permitir simulação de login
    users = ListUsersUseCase(_get_user_repo()).execute()
    
    current_user_id = session.get("user_id")
    current_user = None
    if current_user_id:
        current_user = _get_user_repo().find_by_id(current_user_id)
        
    return render_template(
        "groups.html",
        groups=groups,
        users=users,
        current_user=current_user,
    )


@group_bp.route("/groups/select_user", methods=["POST"])
def select_user():
    """Define o usuário simulado atual na sessão."""
    user_id = request.form.get("user_id")
    if user_id:
        user = _get_user_repo().find_by_id(int(user_id))
        if user:
            session["user_id"] = user.id
            session["user_name"] = user.name
    else:
        session.pop("user_id", None)
        session.pop("user_name", None)
    return redirect(url_for("groups.list_groups"))


@group_bp.route("/groups/new", methods=["GET", "POST"])
def add_group():
    """HU-03: Formulário para criar grupo."""
    error = None
    users = ListUsersUseCase(_get_user_repo()).execute()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        created_by = request.form.get("created_by")
        members = request.form.getlist("members")
        
        try:
            if not created_by:
                raise ValueError("O criador do grupo deve ser especificado.")
            
            created_by_id = int(created_by)
            member_ids = [int(m) for m in members]
            
            use_case = CreateGroupUseCase(_get_group_repo(), _get_user_repo())
            group = use_case.execute(name, created_by_id, member_ids)
            return redirect(url_for("groups.group_detail", group_id=group.id))
        except (ValueError, TypeError) as exc:
            error = str(exc)
            
    return render_template("add_group.html", users=users, error=error)


@group_bp.route("/groups/<int:group_id>")
def group_detail(group_id: int):
    """HU-05: Detalhes do grupo, despesas e resumo de dívidas."""
    group_repo = _get_group_repo()
    user_repo = _get_user_repo()
    
    group = GetGroupDetailsUseCase(group_repo).execute(group_id)
    if not group:
        return "Grupo não encontrado", 404
        
    members = group_repo.get_members(group_id)
    
    from infra.repositories.expense_repository_sqlite import ExpenseRepositorySQLite
    expense_repo = ExpenseRepositorySQLite()
    
    # HU-07: Listar despesas do grupo
    expenses = ListExpensesUseCase(expense_repo).execute(group_id)
    
    # HU-08: Calcular resumo de dívidas
    debts = SummaryUseCase(expense_repo, user_repo, group_repo).execute(group_id)
    
    # Mapear IDs de usuários para nomes para exibição
    users_map = {u.id: u.name for u in members}
    
    # Calcular saldos individuais líquidos no grupo
    # balance[user_id] = saldo líquido
    balances = {}
    for member in members:
        balances[member.id] = 0.0
        
    for expense in expenses:
        share = expense.share_per_person()
        balances[expense.paid_by_user_id] += expense.amount
        for uid in expense.participant_ids:
            balances[uid] -= share
            
    return render_template(
        "group_detail.html",
        group=group,
        members=members,
        expenses=expenses,
        debts=debts,
        users_map=users_map,
        balances=balances,
    )
