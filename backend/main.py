from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from typing import List, Optional
from pydantic import validator

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
class RegisterRequest(BaseModel):
    mobile_number: str

class RegisterResponse(BaseModel):
    message: str
    secret: str

class LoginRequest(BaseModel):
    mobile_number: str
    otp: str

class UserResponse(BaseModel):
    id: int
    mobile_number: str
    employee_id: str | None = None
    role: str

    class Config:
        from_attributes = True

import pyotp

@app.post("/api/auth/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()

    if not user:
        # Auto-create user if they don't exist for prototype
        secret = pyotp.random_base32()
        user = models.User(
            mobile_number=request.mobile_number,
            role="admin" if request.mobile_number == "1234567890" else "employee",
            totp_secret=secret
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if user.totp_secret:
            raise HTTPException(status_code=400, detail="User already registered")
        user.totp_secret = pyotp.random_base32()
        db.commit()
        db.refresh(user)

    return {"message": "User registered successfully", "secret": user.totp_secret}

@app.post("/api/auth/login", response_model=UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()

    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="User not found or not registered for TOTP")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    return user

class BookItemSchema(BaseModel):
    barcode: str
    serial_number: str
    book_id: int | None = None
    order_id: int | None = None
    state: str
    title: str | None = None
    author: str | None = None
    date_of_purchase: str | None = None
    weight: str | None = None
    age_group: str | None = None
    category: str | None = None
    description: str | None = None
    publication_date: str | None = None
    cover_image_url: str | None = None
    last_updated_by: int | None = None
    last_updated: str | None = None

    @validator("date_of_purchase", "last_updated", pre=True)
    def datetime_to_string(cls, v):
        if hasattr(v, 'strftime'):
             return v.strftime("%Y-%m-%d %H:%M:%S")
        return v


    class Config:
        from_attributes = True

class StateUpdateRequest(BaseModel):
    barcode: str
    new_state: str
    agent_id: int

import httpx

@app.get("/api/inventory/{barcode}", response_model=BookItemSchema)
def get_inventory(barcode: str, db: Session = Depends(get_db)):
    item = db.query(models.BookItem).filter(models.BookItem.barcode == barcode).first()
    if not item:
        # Fetch book data from Google Books API
        title = None
        author = None
        description = None
        publication_date = None
        cover_image_url = None

        try:
            # We don't use httpx async here since we are in a def endpoint, so use httpx.get synchronous
            response = httpx.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{barcode}")
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    volume_info = data["items"][0].get("volumeInfo", {})
                    title = volume_info.get("title")
                    authors = volume_info.get("authors", [])
                    author = ", ".join(authors) if authors else None
                    description = volume_info.get("description")
                    publication_date = volume_info.get("publishedDate")
                    image_links = volume_info.get("imageLinks", {})
                    cover_image_url = image_links.get("thumbnail")
        except Exception as e:
            print(f"Error fetching from Google Books: {e}")

        book = db.query(models.Book).filter(models.Book.isbn == barcode).first()
        if not book:
            book = models.Book(
                isbn=barcode,
                title=title,
                author=author,
                description=description,
                publication_date=publication_date,
                cover_image_url=cover_image_url
            )
            db.add(book)
            db.commit()
            db.refresh(book)
        else:
            # Fallback to existing book data if API fetch failed
            if not title:
                title = book.title
            if not author:
                author = book.author
            if not description:
                description = book.description
            if not publication_date:
                publication_date = book.publication_date
            if not cover_image_url:
                cover_image_url = book.cover_image_url

        item = models.BookItem(
            barcode=barcode,
            serial_number=f"SN-{barcode}",
            state="Available",
            book_id=book.id,
            title=title,
            author=author,
            description=description,
            publication_date=publication_date,
            cover_image_url=cover_image_url
        )
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


class HistorySchema(BaseModel):
    state: str
    timestamp: str
    updated_by: str | None = None

    class Config:
        from_attributes = True

@app.get("/api/inventory/{barcode}/history", response_model=List[HistorySchema])
def get_inventory_history(barcode: str, db: Session = Depends(get_db)):
    item = db.query(models.BookItem).filter(models.BookItem.barcode == barcode).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    history_records = db.query(models.StateHistory).filter(models.StateHistory.item_id == item.id).order_by(models.StateHistory.timestamp.desc()).all()

    result = []
    for record in history_records:
        agent_name = "System"
        if record.updated_by:
            agent = db.query(models.User).filter(models.User.id == record.updated_by).first()
            if agent:
                 agent_name = agent.employee_id or agent.mobile_number

        result.append({
            "state": record.state,
            "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(record.timestamp, 'strftime') else str(record.timestamp),
            "updated_by": agent_name
        })
    return result

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
