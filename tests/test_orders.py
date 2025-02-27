import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import OrderType, OrderStatus

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_order(client):
    response = client.post(
        "/orders",
        json={
            "symbol": "AAPL",
            "price": 150.0,
            "quantity": 10,
            "order_type": "MARKET"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 150.0
    assert data["quantity"] == 10
    assert data["order_type"] == "MARKET"
    assert data["status"] == "PENDING"
    assert "id" in data

def test_get_orders(client):
    # Create some orders first
    for i in range(3):
        client.post(
            "/orders",
            json={
                "symbol": f"SYMBOL{i}",
                "price": 100.0 + i,
                "quantity": 10 + i,
                "order_type": "MARKET"
            },
        )
    
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "count" in data
    assert data["count"] == 3
    assert len(data["orders"]) == 3

def test_get_order(client):
    # Create an order first
    create_response = client.post(
        "/orders",
        json={
            "symbol": "MSFT",
            "price": 300.0,
            "quantity": 5,
            "order_type": "LIMIT"
        },
    )
    order_id = create_response.json()["id"]
    
    # Get the order
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["symbol"] == "MSFT"
    assert data["price"] == 300.0
    assert data["quantity"] == 5
    assert data["order_type"] == "LIMIT"

def test_update_order_status(client):
    # Create an order first
    create_response = client.post(
        "/orders",
        json={
            "symbol": "GOOGL",
            "price": 2500.0,
            "quantity": 2,
            "order_type": "MARKET"
        },
    )
    order_id = create_response.json()["id"]
    
    # Update the order status
    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "FILLED"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "FILLED"

def test_order_not_found(client):
    response = client.get("/orders/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"