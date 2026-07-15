from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from typing import List, Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MonkeyBarrow Inventory Management")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class LoginRequest(BaseModel):
    mobile_number: str
    otp: str # For simplicity, any OTP works in this prototype

class UserResponse(BaseModel):
    id: int
    mobile_number: str
    employee_id: str | None = None
    role: str

    class Config:
        from_attributes = True

@app.post("/api/auth/login", response_model=UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    if request.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()
    if not user:
        # For prototype, auto-create user if they don't exist
        raise HTTPException(status_code=400, detail="User not found")

    # In a real app, verify OTP here.
    return user

class BookItemSchema(BaseModel):
    barcode: str
    serial_number: str
    book_id: int | None = None
    order_id: int | None = None
    state: str

    class Config:
        from_attributes = True

class StateUpdateRequest(BaseModel):
    barcode: str
    new_state: str
    agent_id: int

@app.get("/api/inventory/{barcode}", response_model=BookItemSchema)
def get_inventory(barcode: str, db: Session = Depends(get_db)):
    item = db.query(models.BookItem).filter(models.BookItem.barcode == barcode).first()
    if not item:
        # Mocking an external API fetch for new items
        item = models.BookItem(barcode=barcode, serial_number=f"SN-{barcode}", state="Available")
        db.add(item)
        db.commit()
        db.refresh(item)
    return item

@app.patch("/api/inventory/state")
def update_inventory(request: StateUpdateRequest, db: Session = Depends(get_db)):
    item = db.query(models.BookItem).filter(models.BookItem.barcode == request.barcode).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    valid_transitions = {
        "Available": ["Ordered", "Damage/Repair"],
        "Ordered": ["Out for Delivery", "Damage/Repair"],
        "Out for Delivery": ["Delivered", "Damage/Repair"],
        "Delivered": ["Returned"],
        "Returned": ["Sanitization", "Damage/Repair"],
        "Sanitization": ["Available"],
        "Damage/Repair": ["Available"]
    }

    if request.new_state not in valid_transitions.get(item.state, []):
        raise HTTPException(status_code=400, detail=f"Invalid transition from {item.state} to {request.new_state}")

    item.state = request.new_state
    item.last_updated_by = request.agent_id

    # Record history
    history = models.StateHistory(item_id=item.id, state=request.new_state, updated_by=request.agent_id)
    db.add(history)

    db.commit()
    db.refresh(item)

    # Simulation for Shopify stock update via API
    # requests.post("https://{shop}.myshopify.com/admin/api/2023-10/inventory_levels/set.json", ...)
    # Note: the HTTP call would use httpx here in production.
    print(f"MOCKED SHOPIFY UPDATE: Updated {item.barcode} to {item.state} in Shopify")

    return {"message": "State updated successfully", "new_state": item.state}

class EmployeeRequest(BaseModel):
    mobile_number: str
    employee_id: str
    status: str

@app.post("/api/admin/employee", response_model=UserResponse)
def add_employee(request: EmployeeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = models.User(
        mobile_number=request.mobile_number,
        employee_id=request.employee_id,
        role="employee",
        status=request.status
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Shopify Webhook endpoint for 'orders/create'
class ShopifyCustomerInfo(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    default_address: Optional[dict] = None

class ShopifyLineItem(BaseModel):
    sku: str # Use sku as barcode

class ShopifyOrderWebhookRequest(BaseModel):
    id: int
    name: str # e.g. #1001
    customer: Optional[ShopifyCustomerInfo] = None
    line_items: List[ShopifyLineItem]

@app.post("/api/shopify/order")
def shopify_order_create(webhook_data: ShopifyOrderWebhookRequest, db: Session = Depends(get_db)):
    # Create order
    customer_name = "Unknown"
    customer_mobile = None
    customer_address = None

    if webhook_data.customer:
        customer_name = f"{webhook_data.customer.first_name} {webhook_data.customer.last_name}".strip()
        customer_mobile = webhook_data.customer.phone
        if webhook_data.customer.default_address:
            address_parts = [
                webhook_data.customer.default_address.get("address1", ""),
                webhook_data.customer.default_address.get("city", ""),
                webhook_data.customer.default_address.get("country", "")
            ]
            customer_address = ", ".join(filter(bool, address_parts))

    new_order = models.Order(
        shopify_order_id=str(webhook_data.id),
        customer_name=customer_name,
        customer_mobile=customer_mobile,
        customer_address=customer_address
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Process line items
    for line_item in webhook_data.line_items:
        # Link barcode/sku
        item = db.query(models.BookItem).filter(models.BookItem.barcode == line_item.sku).first()
        if item:
            item.state = "Ordered"
            item.order_id = new_order.id
            db.add(models.StateHistory(item_id=item.id, state="Ordered"))

    db.commit()

    return {"message": "Order processed successfully", "order_id": new_order.id}
