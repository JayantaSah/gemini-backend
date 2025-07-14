from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Chatroom(Base):
    __tablename__ = "chatrooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chatrooms")
    messages = relationship("Message", back_populates="chatroom", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chatroom(id={self.id}, title={self.title}, user_id={self.user_id})>"

