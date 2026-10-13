"""
Backend for TOTP based Authentication . 
This program is provides limited functionality for login of an employee 
No new registration is possible.
New employee registration is only possible via admin from Admin screen.
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pyotp
import models
import schemas
from database import SessionLocal

import jwt, datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#--------------------------------------
# 1. Register 
# This module will not be called from frontend as the register request is not defined on frontend
# Limited only to create admin and then admin can add employees
#--------------------------------------
@router.post("/register", response_model=schemas.RegisterResponse)
def register(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()

    if not user:
        secret = pyotp.random_base32()
        user = models.User(
            mobile_number=request.mobile_number,
            role="admin" if request.mobile_number == "8879578999" else "employee",
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

#--------------------------------------
# 1. Login
# This module will be called everytime an employee logs in to the system 
# If the user is admin, then admin page will render else e,ployee page will render.
# Only diffrence between admin page and employee page is capability to add new employee or update employee status
#--------------------------------------
@router.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User Not Found!! {user}")
        #raise HTTPException(status_code=404, detail="User Not Found!!", str(user))   
    # 2. Check employment status
    if user.employment_status in ["not in firm", "suspended"]:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    # 3. Check TOTP secret
    if not user.totp_secret:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    # 4. Verify OTP
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")


    token = jwt.encode(
        {"employee_id": user.employee_id, "role": user.role, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
        "SECRET_KEY",
        algorithm="HS256"
    )
    # If all checks pass, return user
    print(f"employee details api {user.employee_id}")
    print(f"employee details api {token},{user.role}")
    
    return {"access_token": token, "role": user.role}
    
    


    
    #----------------------------------------------
    # End of Program # SM: 28 July 2026
    #----------------------------------------------