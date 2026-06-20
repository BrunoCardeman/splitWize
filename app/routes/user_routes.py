"""Rotas Flask para usuários."""
from flask import Blueprint, redirect, render_template, request, url_for

from infra.repositories.user_repository_sqlite import UserRepositorySQLite
from use_cases.user_use_cases import CreateUserUseCase, ListUsersUseCase

user_bp = Blueprint("users", __name__)


def _get_repo():
    return UserRepositorySQLite()


@user_bp.route("/users")
def list_users():
    """HU-01: Exibe lista de usuários."""
    use_case = ListUsersUseCase(_get_repo())
    users = use_case.execute()
    return render_template("users.html", users=users)


@user_bp.route("/users/new", methods=["GET", "POST"])
def add_user():
    """HU-01: Formulário para cadastrar usuário."""
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        try:
            use_case = CreateUserUseCase(_get_repo())
            use_case.execute(name, email)
            return redirect(url_for("users.list_users"))
        except ValueError as exc:
            error = str(exc)
    return render_template("add_user.html", error=error)