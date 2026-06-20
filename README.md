# SplitWize 💸

Gerenciador de Despesas Compartilhadas em Grupo — Trabalho 2 de Engenharia de Software.

A aplicação foi completamente refatorada seguindo princípios de **Clean Code** e **Clean Architecture**, adicionando suporte a múltiplos grupos com isolamento de despesas, saldos consolidados e sistema de notificações/lembretes de pagamentos.

## Tecnologias
- Python 3.10+
- Flask 3.x
- SQLite
- Pytest

## Como rodar a aplicação

```bash
# 1. Entre na pasta
cd splitWize

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode a aplicação
python app/main.py

# 5. Acesse em http://localhost:5000
```

## Como rodar os testes

```bash
# Rodar todos os testes (unitários e integração de rotas)
pytest testes/ -v

# Rodar testes com cobertura de código nos Casos de Uso e Domínio
pytest testes/ --cov=use_cases --cov=domain --cov-report=term-missing
```

## Arquitetura do Projeto

O projeto segue a **Clean Architecture** (Arquitetura Limpa), garantindo desacoplamento de persistência e interfaces:
- **domain/** — Entidades de domínio puras (`User`, `Group`, `Expense`, `Notification`) com suas validações de regras de negócio.
- **use_cases/** — Regras de negócio da aplicação desacopladas de frameworks (ex: simplificação de dívidas, lembretes de cobrança).
- **infra/** — Camada de persistência SQLite e adaptadores de repositório de dados.
- **app/** — Rotas do Flask (Controller/Views), templates HTML/CSS (Jinja2) e simulação de sessão.