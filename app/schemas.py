from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# Auth Schemas
class UserSignup(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class SendOTP(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)


class VerifyOTP(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)
    otp_code: str = Field(..., min_length=6, max_length=6)


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


# User Schemas
class UserResponse(BaseModel):
    id: int
    mobile_number: str
    name: Optional[str]
    email: Optional[str]
    subscription_tier: str
    daily_message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Chatroom Schemas
class ChatroomCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ChatroomResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatroomDetail(ChatroomResponse):
    messages: List['MessageResponse'] = []


# Message Schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionResponse(BaseModel):
    tier: str
    status: Optional[str] = None
    current_period_end: Optional[datetime] = None


# Generic Response Schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[dict] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OTPResponse(BaseModel):
    success: bool = True
    message: str
    otp_code: str  # In production, this should not be returned


# Update forward references
ChatroomDetail.model_rebuild()

