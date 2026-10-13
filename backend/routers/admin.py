"""
Validated on 18th Sept 2026 - SM
Backend for Admin page with following functionality:
1. Employee Data Saving
    Case 1: New employee (mobile number not found) → Insert new record with mobile_number, role, employment_status, 
    and a freshly generated TOTP secret.
    Case 2: Existing employee (mobile number found) → Update only the role or employment_status fields as per the admin’s request.
"""

from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal
import pyotp   # <-- make sure you import pyotp

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#-----------------------
# 1. Logout Response API
#-----------------------
@router.post("/logout")
def logout(response: Response):
    # If using cookies:
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}

#-----------------------
# 2. Employee Add/Update  Response API
#-----------------------

@router.post("/employee", response_model=schemas.EmployeeResponse)
def add_or_update_employee(request: schemas.EmployeeRequest, db: Session = Depends(get_db)):
    # Check if employee already exists
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()

    if not user:
        # Case 1: New employee → insert with TOTP secret
        secret = pyotp.random_base32()
        new_user = models.User(
            mobile_number=request.mobile_number,
            role=request.role,
            employment_status=request.employment_status,
            totp_secret=secret
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        # Case 2: Existing employee → update role or employment_status
        if request.role:
            user.role = request.role
        if request.employment_status:
            user.employment_status = request.employment_status
        db.commit()
        db.refresh(user)
        return user
    
    #----------------------------------------------
    # End of Program # SM: 28 July 2026
    #----------------------------------------------