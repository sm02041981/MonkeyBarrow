
"""
    SM:05th August 2026
    This program is backend for Update Inventory State, This program includes the following functionalities:
    Case 2: Update Inventory State
    This program will change only Book_Item and Book_state_history table
"""

import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------
# GET ITEM BY 20-DIGIT SERIAL NUMBER
# --------------------------------------
@router.get("/item/{serial_number}")
def get_item_by_serial(serial_number: str, db: Session = Depends(get_db)):
    print(f"I am in isbn api with serial_number {serial_number}")
    if len(serial_number) != 20 or not serial_number.isdigit():
        raise HTTPException(
            status_code=400, 
            detail="Invalid serial_number. Please scan or enter a 20-digit Serial Number."
        )


    item = db.query(models.BookItem).filter(models.BookItem.serial_number == serial_number).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Serial number not found in book_item database")

    print(f"I am in isbn api with serial_number {item.serial_number}")
    return {
        "serial_number": item.serial_number,
        "item_mb_isbn13": item.item_mb_isbn13,
        "item_location": item.item_location,
        "date_of_purchase": str(item.date_of_purchase) if item.date_of_purchase else None,
        "order_id": item.order_id,
        "state": item.state,
        "last_updated": str(item.last_updated) if item.last_updated else None,
        "last_updated_by": item.last_updated_by
    
    }

# ---------------------------------------
# UPDATE ITEM STATE / LOCATION / ORDER ID
# ---------------------------------------
@router.patch("/stateupdate")
def update_inventory(request: schemas.StateUpdateRequest, db: Session = Depends(get_db)):
    if len(request.serial_number) != 20 or not request.serial_number.isdigit():
        raise HTTPException(
            status_code=400, 
            detail="Invalid serial number. Must be exactly 20 digits."
        )

    item = db.query(models.BookItem).filter(models.BookItem.serial_number == request.serial_number).first()
    if not item:
        raise HTTPException(status_code=404, detail="Book item not found")

    valid_transitions = {
        "Available": ["Ordered", "Damage/Repair"],
        "Ordered": ["Out for Delivery", "Damage/Repair"],
        "Out for Delivery": ["Delivered", "Damage/Repair"],
        "Delivered": ["Returned", "Damage/Repair"],
        "Returned": ["Sanitization", "Damage/Repair"],
        "Sanitization": ["Available"],
        "Damage/Repair": ["Available"]
    }

    now = datetime.datetime.utcnow()

    # 1. Update State (if passed)
    if request.new_state and request.new_state != item.state:
        allowed = valid_transitions.get(item.state, [])
        if request.new_state not in allowed:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid state transition from '{item.state}' to '{request.new_state}'"
            )
        item.state = request.new_state

    # 2. Update Location (if passed)
    if request.new_location is not None and request.new_location.strip() != "":
        item.item_location = request.new_location.strip()

    # 3. Update Order ID (if passed)
    if request.order_id is not None:
        item.order_id = request.order_id

    item.last_updated = now
    item.last_updated_by = request.employee_id

    # 4. Log state history entry
    history_entry = models.BookStateHistory(
        book_item_serial_number=item.serial_number,
        state=item.state,
        state_timestamp=now,
        state_updated_by=request.employee_id,
        state_item_location=item.item_location
    )
       
    db.add(history_entry)

    try:
        db.commit()
        db.refresh(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")

    return {
        "message": "Item updated successfully",
        "serial_number": item.serial_number,
        "state": item.state,
        "item_location": item.item_location,
        "order_id": item.order_id
    }