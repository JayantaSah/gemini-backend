from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False)  # 'login', 'signup', 'reset'
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OTP(id={self.id}, mobile_number={self.mobile_number}, purpose={self.purpose})>"

