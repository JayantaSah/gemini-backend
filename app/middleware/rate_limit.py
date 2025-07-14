from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.config import settings


def check_rate_limit(user: User, db: Session) -> None:
    """Check if user has exceeded daily message limit"""
    today = date.today()
    
    # Reset daily count if it's a new day
    if user.last_message_date != today:
        user.daily_message_count = 0
        user.last_message_date = today
        db.commit()
    
    # Check limits based on subscription tier
    if user.subscription_tier == "basic":
        daily_limit = settings.basic_daily_limit
    else:  # pro
        daily_limit = settings.pro_daily_limit
    
    if user.daily_message_count >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily message limit exceeded. Upgrade to Pro for unlimited messages."
        )


def increment_message_count(user: User, db: Session) -> None:
    """Increment user's daily message count"""
    user.daily_message_count += 1
    db.commit()

