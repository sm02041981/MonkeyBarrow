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

import pyotp

def test_register_and_login():
    # 1. Register to get the TOTP secret
    response = client.post("/api/auth/register", json={"mobile_number": "1234567890"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"
    secret = data["secret"]
    assert secret is not None
    assert len(secret) > 0

    # 2. Login using the TOTP secret
    totp = pyotp.TOTP(secret)
    current_otp = totp.now()

    response = client.post("/api/auth/login", json={"mobile_number": "1234567890", "otp": current_otp})
    assert response.status_code == 200
    assert response.json()["mobile_number"] == "1234567890"

    # 3. Test invalid OTP
    response = client.post("/api/auth/login", json={"mobile_number": "1234567890", "otp": "000000"})
    assert response.status_code == 400

from unittest.mock import patch

@patch("httpx.get")
def test_get_inventory(mock_get):
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Mock Book Title",
                            "authors": ["Author One", "Author Two"],
                            "description": "A great mock book.",
                            "publishedDate": "2023-01-01",
                            "imageLinks": {
                                "thumbnail": "http://example.com/cover.jpg"
                            }
                        }
                    }
                ]
            }
    mock_get.return_value = MockResponse()

    response = client.get("/api/inventory/TEST_BARCODE")
    assert response.status_code == 200
    data = response.json()
    assert data["barcode"] == "TEST_BARCODE"
    assert data["state"] == "Available"
    assert data["title"] == "Mock Book Title"
    assert data["author"] == "Author One, Author Two"
    assert data["description"] == "A great mock book."
    assert data["publication_date"] == "2023-01-01"
    assert data["cover_image_url"] == "http://example.com/cover.jpg"

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
