from fastapi import APIRouter, Depends
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
