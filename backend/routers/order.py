""" 
Below is life cycle of an order & by default we are generating order when we receive order from shopify or from app.
So default / start state of order = "Ordered" and End-state is "Closed".
Lifecycle with sequence is as follows:
1. default="Ordered" #Initial Stage
2. "Processing"  #Intermediary Stage
3. "Out-For-Delivery"  #Intermediary Stage
4. "Full-Inventory-Delivered-To-Cust"  #Intermediary Stage
5. "Partial-Inventory-Delivered-To-Cust"  #Intermediary Stage
6. "Full-Inventory-Returned-By-Cust"  #Intermediary Stage
7. "Partial-Inventory-Returned-By-Cust"  #Intermediary Stage
8. "Cancelled-By-Cust" #Final Stage
9. "Rejected-By-Store" #Final Stage
10."Closed" #Final Stage

valid_transitions = {
        "Ordered": ["Processing", "Cancelled-By-Cust","Rejected-By-Store"],
        "Processing": ["Out for Delivery", "Cancelled-By-Cust","Rejected-By-Store"],
        "Out for Delivery": ["Full-Inventory-Delivered-To-Cust", "Partial-Inventory-Delivered-To-Cust", "Cancelled-By-Cust","Rejected-By-Store"],
        "Full-Inventory-Delivered-To-Cust": ["Full-Inventory-Returned-By-Cust", "Partial-Inventory-Returned-By-Cust"],
        "Partial-Inventory-Delivered-To-Cust": ["Partial-Inventory-Returned-By-Cust"],"Delivered": ["Returned", "Cancelled-By-Cust","Rejected-By-Store"],
        "Full-Inventory-Returned-By-Cust": ["Closed"],
        "Partial-Inventory-Returned-By-Cust": ["Closed"],
        "Rejected-By-Store": ["Rejected-By-Store"],
        "Cancelled-By-Cust": ["Cancelled-By-Cust"]
    }
    
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# -------------------------
# Logout Endpoint
# -------------------------

@router.post("/logout")
def logout(response: Response):
    # If using cookies:
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}


@router.post("/order")
def shopify_order_create(webhook_data: schemas.ShopifyOrderWebhookRequest, db: Session = Depends(get_db)):
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

    for line_item in webhook_data.line_items:
        item = db.query(models.BookItem).filter(models.BookItem.barcode == line_item.sku).first()
        if item:
            item.state = "Ordered"
            item.order_id = new_order.id
            db.add(models.StateHistory(item_id=item.id, state="Ordered"))

    db.commit()

    return {"message": "Order processed successfully", "order_id": new_order.id}
