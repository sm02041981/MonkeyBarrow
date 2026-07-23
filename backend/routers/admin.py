from fastapi import APIRouter, Depends, HTTPException
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

@router.post("/employee", response_model=schemas.UserResponse)
def add_employee(request: schemas.EmployeeRequest, db: Session = Depends(get_db)):
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
