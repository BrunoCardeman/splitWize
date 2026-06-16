# SplitFácil 💸

Gerenciador de Despesas Compartilhadas — Trabalho 2 de Engenharia de Software.

## Tecnologias
- Python 3.10+
- Flask 3.x
- SQLite
- Pytest

## Como rodar

```bash
# 1. Clone e entre na pasta
git clone <url-do-repo>
cd splitfacil

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode a aplicação
python app/main.py

# 5. Acesse em http://localhost:5000
```

## Testes

```bash
pytest tests/ -v
pytest tests/ --cov=use_cases --cov-report=term-missing
```

## Arquitetura

Projeto organizado em Clean Architecture:
- **domain/** — Entidades puras (User, Expense)
- **use_cases/** — Lógica de negócio isolada
- **infra/** — Persistência SQLite
- **app/** — Rotas Flask e templates HTML