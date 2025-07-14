from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    
    # Get request body and signature
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header"
        )
    
    # Construct webhook event
    event = stripe_service.construct_webhook_event(payload, sig_header)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        await handle_checkout_completed(event['data']['object'], db)
    
    elif event['type'] == 'invoice.payment_succeeded':
        await handle_payment_succeeded(event['data']['object'], db)
    
    elif event['type'] == 'invoice.payment_failed':
        await handle_payment_failed(event['data']['object'], db)
    
    elif event['type'] == 'customer.subscription.updated':
        await handle_subscription_updated(event['data']['object'], db)
    
    elif event['type'] == 'customer.subscription.deleted':
        await handle_subscription_deleted(event['data']['object'], db)
    
    return {"status": "success"}


async def handle_checkout_completed(session, db: Session):
    """Handle successful checkout session completion"""
    customer_id = session['customer']
    subscription_id = session['subscription']
    
    # Find user by Stripe customer ID
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        return
    
    # Get subscription details from Stripe
    subscription_data = stripe_service.get_subscription(subscription_id)
    if not subscription_data:
        return
    
    # Create or update subscription record
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription_id,
            status=subscription_data['status'],
            current_period_start=datetime.fromtimestamp(subscription_data['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription_data['current_period_end'])
        )
        db.add(subscription)
    else:
        subscription.status = subscription_data['status']
        subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
    
    # Update user subscription tier
    user.subscription_tier = "pro"
    
    db.commit()


async def handle_payment_succeeded(invoice, db: Session):
    """Handle successful payment"""
    subscription_id = invoice['subscription']
    
    # Update subscription status
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = "active"
        subscription.user.subscription_tier = "pro"
        db.commit()


async def handle_payment_failed(invoice, db: Session):
    """Handle failed payment"""
    subscription_id = invoice['subscription']
    
    # Update subscription status
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = "past_due"
        db.commit()


async def handle_subscription_updated(subscription_obj, db: Session):
    """Handle subscription updates"""
    subscription_id = subscription_obj['id']
    
    # Update subscription record
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = subscription_obj['status']
        subscription.current_period_start = datetime.fromtimestamp(subscription_obj['current_period_start'])
        subscription.current_period_end = datetime.fromtimestamp(subscription_obj['current_period_end'])
        
        # Update user tier based on status
        if subscription_obj['status'] == 'active':
            subscription.user.subscription_tier = "pro"
        else:
            subscription.user.subscription_tier = "basic"
        
        db.commit()


async def handle_subscription_deleted(subscription_obj, db: Session):
    """Handle subscription cancellation"""
    subscription_id = subscription_obj['id']
    
    # Update subscription record
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = "canceled"
        subscription.user.subscription_tier = "basic"
        db.commit()

