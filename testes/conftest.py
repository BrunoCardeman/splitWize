import os
import tempfile
import pytest

from app.main import create_app
from infra.db import database


@pytest.fixture
def client():
    """Configura um cliente de teste Flask com banco SQLite temporário isolado."""
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    original_db_path = database.DB_PATH
    database.DB_PATH = temp_db_path

    # Inicializa as tabelas no banco de dados temporário
    database.init_db()

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client

    # Fecha e remove o banco de dados temporário
    os.close(temp_db_fd)
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except PermissionError:
            pass
    database.DB_PATH = original_db_path
