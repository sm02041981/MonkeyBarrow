from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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

@router.get("/{barcode}", response_model=schemas.BookItemSchema)
def get_inventory(barcode: str, db: Session = Depends(get_db)):
    item = db.query(models.BookItem).filter(models.BookItem.barcode == barcode).first()
    if not item:
        item = models.BookItem(barcode=barcode, serial_number=f"SN-{barcode}", state="Available")
        db.add(item)
        db.commit()
        db.refresh(item)
    return item

@router.patch("/state")
def update_inventory(request: schemas.StateUpdateRequest, db: Session = Depends(get_db)):
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

    history = models.StateHistory(item_id=item.id, state=request.new_state, updated_by=request.agent_id)
    db.add(history)

    db.commit()
    db.refresh(item)

    print(f"MOCKED SHOPIFY UPDATE: Updated {item.barcode} to {item.state} in Shopify")

    return {"message": "State updated successfully", "new_state": item.state}


@router.get("/{barcode}/history", response_model=List[schemas.HistorySchema])
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
