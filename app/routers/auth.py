from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.otp import OTP
from app.schemas import (
    UserSignup, SendOTP, VerifyOTP, ChangePassword,
    TokenResponse, OTPResponse, SuccessResponse, UserResponse
)
from app.utils.auth import create_access_token, get_password_hash, verify_password
from app.utils.otp import generate_otp, get_otp_expiry, is_otp_valid
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SuccessResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user with mobile number"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.mobile_number == user_data.mobile_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists"
        )
    
    # Create new user
    user = User(
        mobile_number=user_data.mobile_number,
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password) if user_data.password else None
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return SuccessResponse(
        message="User registered successfully",
        data={"user_id": user.id}
    )


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(otp_request: SendOTP, db: Session = Depends(get_db)):
    """Send OTP to user's mobile number (mocked)"""
    
    # Check if user exists
    user = db.query(User).filter(User.mobile_number == otp_request.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = get_otp_expiry()
    
    # Save OTP to database
    otp = OTP(
        mobile_number=otp_request.mobile_number,
        otp_code=otp_code,
        purpose="login",
        expires_at=expires_at
    )
    
    db.add(otp)
    db.commit()
    
    # In production, send OTP via SMS service
    # For now, return OTP in response (development only)
    return OTPResponse(
        message="OTP sent successfully",
        otp_code=otp_code  # Remove this in production
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(otp_data: VerifyOTP, db: Session = Depends(get_db)):
    """Verify OTP and return JWT token"""
    
    # Find valid OTP
    otp = db.query(OTP).filter(
        OTP.mobile_number == otp_data.mobile_number,
        OTP.otp_code == otp_data.otp_code,
        OTP.purpose == "login",
        OTP.is_used == False
    ).first()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Check if OTP is expired
    if not is_otp_valid(otp.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired"
        )
    
    # Mark OTP as used
    otp.is_used = True
    db.commit()
    
    # Get user
    user = db.query(User).filter(User.mobile_number == otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/forgot-password", response_model=OTPResponse)
async def forgot_password(otp_request: SendOTP, db: Session = Depends(get_db)):
    """Send OTP for password reset"""
    
    # Check if user exists
    user = db.query(User).filter(User.mobile_number == otp_request.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = get_otp_expiry()
    
    # Save OTP to database
    otp = OTP(
        mobile_number=otp_request.mobile_number,
        otp_code=otp_code,
        purpose="reset",
        expires_at=expires_at
    )
    
    db.add(otp)
    db.commit()
    
    return OTPResponse(
        message="Password reset OTP sent successfully",
        otp_code=otp_code  # Remove this in production
    )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password while logged in"""
    
    # Verify current password
    if not current_user.password_hash or not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return SuccessResponse(message="Password changed successfully")

