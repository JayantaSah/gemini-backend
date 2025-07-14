from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.chatroom import Chatroom
from app.models.message import Message
from app.schemas import (
    ChatroomCreate, ChatroomResponse, ChatroomDetail,
    MessageCreate, MessageResponse, SuccessResponse
)
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import check_rate_limit, increment_message_count
from app.utils.cache import cache_user_chatrooms, get_cached_chatrooms, invalidate_chatroom_cache
from app.services.tasks import process_gemini_message

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


@router.post("", response_model=ChatroomResponse)
async def create_chatroom(
    chatroom_data: ChatroomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chatroom for the authenticated user"""
    
    # Create new chatroom
    chatroom = Chatroom(
        user_id=current_user.id,
        title=chatroom_data.title,
        description=chatroom_data.description
    )
    
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    
    # Invalidate cache
    invalidate_chatroom_cache(current_user.id)
    
    return ChatroomResponse.from_orm(chatroom)


@router.get("", response_model=List[ChatroomResponse])
async def get_user_chatrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chatrooms for the user (with caching)"""
    
    # Try to get from cache first
    cached_chatrooms = get_cached_chatrooms(current_user.id)
    if cached_chatrooms:
        return [ChatroomResponse(**chatroom) for chatroom in cached_chatrooms]
    
    # Query database with message count
    chatrooms_query = db.query(
        Chatroom,
        func.count(Message.id).label('message_count')
    ).outerjoin(Message).filter(
        Chatroom.user_id == current_user.id
    ).group_by(Chatroom.id).order_by(Chatroom.updated_at.desc())
    
    chatrooms_with_count = chatrooms_query.all()
    
    # Prepare response data
    chatrooms_data = []
    for chatroom, message_count in chatrooms_with_count:
        chatroom_dict = {
            "id": chatroom.id,
            "title": chatroom.title,
            "description": chatroom.description,
            "created_at": chatroom.created_at,
            "updated_at": chatroom.updated_at,
            "message_count": message_count or 0
        }
        chatrooms_data.append(chatroom_dict)
    
    # Cache the results
    cache_user_chatrooms(current_user.id, chatrooms_data)
    
    return [ChatroomResponse(**chatroom) for chatroom in chatrooms_data]


@router.get("/{chatroom_id}", response_model=ChatroomDetail)
async def get_chatroom_detail(
    chatroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific chatroom"""
    
    # Get chatroom
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.chatroom_id == chatroom_id
    ).order_by(Message.created_at.asc()).all()
    
    # Prepare response
    chatroom_detail = ChatroomDetail(
        id=chatroom.id,
        title=chatroom.title,
        description=chatroom.description,
        created_at=chatroom.created_at,
        updated_at=chatroom.updated_at,
        message_count=len(messages),
        messages=[MessageResponse.from_orm(msg) for msg in messages]
    )
    
    return chatroom_detail


@router.post("/{chatroom_id}/message", response_model=SuccessResponse)
async def send_message(
    chatroom_id: int,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and receive a Gemini response (via queue/async call)"""
    
    # Check if chatroom exists and belongs to user
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Check rate limits
    check_rate_limit(current_user, db)
    
    # Save user message
    user_message = Message(
        chatroom_id=chatroom_id,
        content=message_data.content,
        role="user"
    )
    
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Increment message count
    increment_message_count(current_user, db)
    
    # Queue Gemini API call
    task = process_gemini_message.delay(
        chatroom_id=chatroom_id,
        user_message=message_data.content,
        message_id=user_message.id
    )
    
    # Update chatroom timestamp
    chatroom.updated_at = func.now()
    db.commit()
    
    # Invalidate cache
    invalidate_chatroom_cache(current_user.id)
    
    return SuccessResponse(
        message="Message sent successfully. AI response is being generated.",
        data={
            "message_id": user_message.id,
            "task_id": task.id
        }
    )

