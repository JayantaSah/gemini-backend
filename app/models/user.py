from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), unique=True, index=True, nullable=False)
    name = Column(String(100))
    email = Column(String(255))
    password_hash = Column(String(255))
    subscription_tier = Column(String(20), default="basic")
    daily_message_count = Column(Integer, default=0)
    last_message_date = Column(Date)
    stripe_customer_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    chatrooms = relationship("Chatroom", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, mobile_number={self.mobile_number})>"

