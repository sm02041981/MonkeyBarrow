from fastapi.testclient import TestClient
from main import app, get_db
from database import Base, engine, SessionLocal
import models
import pytest
from sqlalchemy.orm import Session

# Setup test DB
models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_generate_otp():
    response = client.post("/api/auth/generate-otp", json={"mobile_number": "1234567890"})
    assert response.status_code == 200
    assert response.json()["message"] == "OTP generated and sent successfully"

def test_login():
    # Create mock user for test
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.mobile_number=="1234567890").first()
    if not user:
        db.add(models.User(mobile_number="1234567890", role="admin"))
        db.commit()
    db.close()
    response = client.post("/api/auth/login", json={"mobile_number": "1234567890", "otp": "123456"})
    assert response.status_code == 200
    assert response.json()["mobile_number"] == "1234567890"

def test_get_inventory():
    response = client.get("/api/inventory/TEST_BARCODE")
    assert response.status_code == 200
    assert response.json()["barcode"] == "TEST_BARCODE"
    assert response.json()["state"] == "Available"

def test_update_inventory():
    # First get it so it's created
    client.get("/api/inventory/TEST_UPDATE")

    # cleanup from previous tests
    db = SessionLocal()
    item = db.query(models.BookItem).filter(models.BookItem.barcode=="TEST_UPDATE").first()
    if item:
        item.state = "Available"
        db.commit()
    db.close()

    # Valid transition: Available -> Ordered
    response = client.patch("/api/inventory/state", json={"barcode": "TEST_UPDATE", "new_state": "Ordered", "agent_id": 1})
    assert response.status_code == 200
    assert response.json()["new_state"] == "Ordered"

    # Invalid transition: Ordered -> Returned
    response = client.patch("/api/inventory/state", json={"barcode": "TEST_UPDATE", "new_state": "Returned", "agent_id": 1})
    assert response.status_code == 400

def test_shopify_order_webhook():
    # Setup dummy available item
    client.get("/api/inventory/SKU123")

    # cleanup order from previous runs
    db = SessionLocal()
    order = db.query(models.Order).filter(models.Order.shopify_order_id=="9999").first()
    if order:
        db.delete(order)
        db.commit()
    db.close()

    webhook_payload = {
        "id": 9999,
        "name": "#1001",
        "customer": {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "555-1234",
            "default_address": {
                "address1": "123 Main St",
                "city": "Anytown",
                "country": "USA"
            }
        },
        "line_items": [
            {"sku": "SKU123"}
        ]
    }

    response = client.post("/api/shopify/order", json=webhook_payload)
    assert response.status_code == 200

    # Verify the item state was updated to Ordered
    item_response = client.get("/api/inventory/SKU123")
    assert item_response.json()["state"] == "Ordered"
