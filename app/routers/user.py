from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas import UserResponse
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get details about the currently authenticated user"""
    return UserResponse.from_orm(current_user)

