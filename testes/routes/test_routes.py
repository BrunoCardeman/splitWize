"""Testes de integração para as rotas do Flask."""


def test_index_redirects_to_groups(client):
    """A rota raiz (/) deve redirecionar para a lista de grupos."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/groups" in response.headers["Location"]


def test_user_creation_and_listing(client):
    """Deve cadastrar um usuário via POST e listá-lo via GET."""
    # 1. Listar usuários inicialmente (deve estar vazio)
    response = client.get("/users")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Nenhum usuário cadastrado" in html

    # 2. Criar novo usuário
    response = client.post("/users/new", data={
        "name": "Ana Silva",
        "email": "ana@email.com"
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Ana Silva" in html
    assert "ana@email.com" in html


def test_group_creation_and_details(client):
    """Deve cadastrar usuários, criar um grupo com eles e visualizar os detalhes."""
    # 1. Cadastrar usuários de teste
    client.post("/users/new", data={"name": "Ana", "email": "ana@e.com"})
    client.post("/users/new", data={"name": "Bob", "email": "bob@e.com"})

    # 2. Criar o grupo
    response = client.post("/groups/new", data={
        "name": "Viagem de Fim de Semana",
        "created_by": "1",  # ID do criador (Ana)
        "members": ["1", "2"]  # IDs dos participantes (Ana, Bob)
    }, follow_redirects=True)
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Viagem de Fim de Semana" in html
    assert "Ana" in html
    assert "Bob" in html


def test_expense_creation_and_balance_calculation(client):
    """Deve criar despesa em um grupo e calcular o saldo líquido de cada um."""
    # 1. Criar usuários e grupo
    client.post("/users/new", data={"name": "Ana", "email": "ana@e.com"}) # ID 1
    client.post("/users/new", data={"name": "Bob", "email": "bob@e.com"}) # ID 2
    client.post("/groups/new", data={
        "name": "Churrasco",
        "created_by": "1",
        "members": ["1", "2"]
    }) # ID 1

    # 2. Adicionar uma despesa (Ana pagou R$ 60 dividindo com Bob)
    response = client.post("/groups/1/expenses/new", data={
        "description": "Carnes e Bebidas",
        "amount": "60.00",
        "paid_by": "1",
        "participants": ["1", "2"]
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Deve aparecer na lista de despesas
    assert "Carnes e Bebidas" in html
    assert "R$ 60.00" in html
    
    # Deve constar que Bob deve R$ 30.00 para Ana no acerto de contas
    assert "Bob" in html
    assert "deve pagar" in html
    assert "Ana" in html
    assert "R$ 30.00" in html

    # Deve mostrar saldo consolidado (+30 para Ana, -30 para Bob)
    assert "+ R$ 30.00" in html
    assert "- R$ 30.00" in html


def test_simulated_login_and_notifications(client):
    """Deve simular o login de um usuário e enviar/receber notificações de cobrança."""
    # 1. Setup inicial de usuários e grupo
    client.post("/users/new", data={"name": "Ana", "email": "ana@e.com"}) # ID 1
    client.post("/users/new", data={"name": "Bob", "email": "bob@e.com"}) # ID 2
    client.post("/groups/new", data={
        "name": "Viagem",
        "created_by": "1",
        "members": ["1", "2"]
    }) # ID 1

    # 2. Simular login como Ana (Credora) para poder enviar cobrança
    client.post("/groups/select_user", data={"user_id": "1"})

    # 3. Enviar notificação de cobrança para Bob (ID 2)
    response = client.post("/notifications/send", data={
        "group_id": "1",
        "from_user_id": "1",
        "to_user_id": "2",
        "amount": "40.00"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Lembrete de pagamento enviado com sucesso!" in html

    # 4. Simular login como Bob (Devedor) para ver a notificação recebida
    client.post("/groups/select_user", data={"user_id": "2"})
    
    # 5. Listar notificações de Bob
    response = client.get("/notifications")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Ana lembrou que você deve R$ 40.00 no grupo" in html
