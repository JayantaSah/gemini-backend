from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant'
    gemini_response_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chatroom = relationship("Chatroom", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, chatroom_id={self.chatroom_id}, role={self.role})>"

