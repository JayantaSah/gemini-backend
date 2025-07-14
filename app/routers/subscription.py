from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas import SubscriptionResponse, SuccessResponse
from app.middleware.auth import get_current_user
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/subscribe", tags=["Subscription"])


@router.post("/pro", response_model=SuccessResponse)
async def subscribe_to_pro(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a Pro subscription via Stripe Checkout"""
    
    # Check if user already has an active subscription
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active Pro subscription"
        )
    
    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer_result = stripe_service.create_customer(
            email=current_user.email or f"{current_user.mobile_number}@example.com",
            mobile_number=current_user.mobile_number
        )
        
        if not customer_result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Stripe customer: {customer_result['error']}"
            )
        
        current_user.stripe_customer_id = customer_result['customer_id']
        db.commit()
    
    # Create checkout session
    success_url = "https://your-frontend-domain.com/subscription/success"
    cancel_url = "https://your-frontend-domain.com/subscription/cancel"
    
    session_result = stripe_service.create_checkout_session(
        customer_id=current_user.stripe_customer_id,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    if not session_result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {session_result['error']}"
        )
    
    return SuccessResponse(
        message="Checkout session created successfully",
        data={
            "checkout_url": session_result['checkout_url'],
            "session_id": session_result['session_id']
        }
    )


@router.get("/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check the user's current subscription tier"""
    
    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if subscription:
        return SubscriptionResponse(
            tier="pro",
            status=subscription.status,
            current_period_end=subscription.current_period_end
        )
    else:
        return SubscriptionResponse(
            tier="basic",
            status=None,
            current_period_end=None
        )

