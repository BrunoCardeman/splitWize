"""Rotas Flask para notificações/lembretes de pagamento."""
from flask import Blueprint, redirect, render_template, request, url_for, session, flash

from infra.repositories.notification_repository_sqlite import NotificationRepositorySQLite
from infra.repositories.user_repository_sqlite import UserRepositorySQLite
from infra.repositories.group_repository_sqlite import GroupRepositorySQLite
from use_cases.notification_use_cases import (
    SendReminderUseCase,
    ListNotificationsUseCase,
    MarkNotificationAsReadUseCase,
)

notification_bp = Blueprint("notifications", __name__)


def _get_notification_repo():
    return NotificationRepositorySQLite()


def _get_user_repo():
    return UserRepositorySQLite()


def _get_group_repo():
    return GroupRepositorySQLite()


@notification_bp.route("/notifications/send", methods=["POST"])
def send_reminder():
    """HU-10: Envia uma notificação/lembrete de pagamento para outro usuário."""
    group_id = request.form.get("group_id")
    from_user_id = request.form.get("from_user_id")
    to_user_id = request.form.get("to_user_id")
    amount_str = request.form.get("amount")

    if not all([group_id, from_user_id, to_user_id, amount_str]):
        flash("Dados incompletos para enviar o lembrete.", "error")
        return redirect(url_for("groups.list_groups"))

    try:
        group_id_int = int(group_id)
        from_user_id_int = int(from_user_id)
        to_user_id_int = int(to_user_id)
        amount = float(amount_str)

        use_case = SendReminderUseCase(
            _get_notification_repo(), _get_user_repo(), _get_group_repo()
        )
        use_case.execute(group_id_int, from_user_id_int, to_user_id_int, amount)
        flash("Lembrete de pagamento enviado com sucesso!", "success")
    except Exception as exc:
        flash(f"Erro ao enviar lembrete: {str(exc)}", "error")

    return redirect(url_for("groups.group_detail", group_id=group_id_int))


@notification_bp.route("/notifications")
def list_notifications():
    """HU-11: Exibe todas as notificações do usuário simulado atual."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Por favor, selecione um usuário para simular e ver as notificações.", "info")
        return redirect(url_for("groups.list_groups"))

    use_case = ListNotificationsUseCase(_get_notification_repo())
    notifications = use_case.execute(user_id)

    # Obter dados de usuários para exibição de remetentes
    user_repo = _get_user_repo()
    users_map = {u.id: u.name for u in user_repo.find_all()}
    
    return render_template(
        "notifications.html",
        notifications=notifications,
        users_map=users_map,
    )


@notification_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
def mark_as_read(notification_id: int):
    """Marca uma notificação como lida."""
    use_case = MarkNotificationAsReadUseCase(_get_notification_repo())
    use_case.execute(notification_id)
    return redirect(url_for("notifications.list_notifications"))
