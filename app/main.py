"""Ponto de entrada da aplicação Flask."""
from flask import Flask, redirect, url_for

from app.routes.user_routes import user_bp
from app.routes.expense_routes import expense_bp
from infra.db.database import init_db


def create_app() -> Flask:
    """Factory que cria e configura a aplicação Flask."""
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "splitfacil-secret-key-2024"

    # Registra blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(expense_bp)

    @app.route("/")
    def index():
        return redirect(url_for("users.list_users"))

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=True)