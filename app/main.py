"""Ponto de entrada da aplicação Flask."""
from flask import Flask, redirect, url_for, session

from app.routes.user_routes import user_bp
from app.routes.expense_routes import expense_bp
from app.routes.group_routes import group_bp
from app.routes.notification_routes import notification_bp
from infra.db.database import init_db


def create_app() -> Flask:
    """Factory que cria e configura a aplicação Flask."""
    import os
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.environ.get("SECRET_KEY", "splitfacil-secret-key-2024")

    # Registra blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(notification_bp)

    @app.context_processor
    def inject_notifications_count():
        count = 0
        user_id = session.get("user_id")
        if user_id:
            try:
                from infra.repositories.notification_repository_sqlite import NotificationRepositorySQLite
                repo = NotificationRepositorySQLite()
                count = repo.count_unread_for_user(user_id)
            except Exception:
                pass
        return dict(unread_notifications_count=count)

    @app.route("/")
    def index():
        return redirect(url_for("groups.list_groups"))

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=True)