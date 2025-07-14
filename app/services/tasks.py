from celery import current_task
from sqlalchemy.orm import Session
from app.services.celery_app import celery_app
from app.services.gemini_service import gemini_service
from app.database import SessionLocal
from app.models.message import Message
from app.models.chatroom import Chatroom
from typing import List, Dict


@celery_app.task(bind=True)
def process_gemini_message(self, chatroom_id: int, user_message: str, message_id: int):
    """Process user message with Gemini API asynchronously"""
    db = SessionLocal()
    try:
        # Update task status
        current_task.update_state(state='PROGRESS', meta={'status': 'Processing message with Gemini API'})
        
        # Get conversation history
        chatroom = db.query(Chatroom).filter(Chatroom.id == chatroom_id).first()
        if not chatroom:
            raise Exception("Chatroom not found")
        
        # Get recent messages for context
        recent_messages = db.query(Message).filter(
            Message.chatroom_id == chatroom_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Prepare conversation history
        conversation_history = []
        for msg in reversed(recent_messages):
            conversation_history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # Generate response from Gemini
        gemini_response = gemini_service.generate_response(
            user_message, 
            conversation_history
        )
        
        # Save Gemini response to database
        assistant_message = Message(
            chatroom_id=chatroom_id,
            content=gemini_response,
            role="assistant",
            gemini_response_id=self.request.id
        )
        db.add(assistant_message)
        db.commit()
        
        return {
            'status': 'completed',
            'message_id': assistant_message.id,
            'response': gemini_response
        }
    
    except Exception as e:
        # Handle errors
        db.rollback()
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
    
    finally:
        db.close()


@celery_app.task
def cleanup_expired_otps():
    """Clean up expired OTP records"""
    from datetime import datetime
    from app.models.otp import OTP
    
    db = SessionLocal()
    try:
        # Delete expired OTPs
        expired_otps = db.query(OTP).filter(
            OTP.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        return f"Cleaned up {expired_otps} expired OTP records"
    
    except Exception as e:
        db.rollback()
        raise
    
    finally:
        db.close()

