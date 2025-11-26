from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from ..core.database import get_db
from ..core.security import create_access_token
from ..core.config import settings
from ..services.user_service import UserService
from ..schemas.user import UserCreate, UserResponse, UserLogin, Token
from ..core.rate_limit import RateLimiter

router = APIRouter(prefix="/auth", tags=["authentication"])
limit_auth = RateLimiter(limit=20, window_seconds=60)

@router.post("/register", response_model=UserResponse, dependencies=[Depends(limit_auth)])
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    user_service = UserService(db)
    try:
        user = await user_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token, dependencies=[Depends(limit_auth)])
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token"""
    user_service = UserService(db)
    user = await user_service.authenticate_user(user_login.email, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = await user_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

# Import dependencies at the bottom to avoid circular imports
from .dependencies import get_current_active_user
