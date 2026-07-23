from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pyotp
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


@router.post("/login", response_model=schemas.UserResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.mobile_number == request.mobile_number).first()

    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="User not found or not registered for TOTP")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    return user
