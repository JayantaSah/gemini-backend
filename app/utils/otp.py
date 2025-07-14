import random
import string
from datetime import datetime, timedelta


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def is_otp_valid(otp_expires_at: datetime) -> bool:
    """Check if OTP is still valid (not expired)"""
    return datetime.utcnow() < otp_expires_at


def get_otp_expiry(minutes: int = 10) -> datetime:
    """Get OTP expiry time (default 10 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=minutes)

