from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..schemas.request import ServiceRequestCreate, ServiceRequestResponse
from ..services.request_service import RequestService
from ..models.models import ServiceRequest, User
from ..core.rate_limit import RateLimiter

router = APIRouter(prefix="/public", tags=["public"])
limit_create = RateLimiter(limit=10, window_seconds=60)
limit_status = RateLimiter(limit=30, window_seconds=60)

async def _get_anonymous_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == "anonymous@system.local"))
    user = result.scalar_one_or_none()
    if user:
        return user
    from ..services.user_service import UserService
    svc = UserService(db)
    from ..schemas.user import UserCreate
    try:
        user = await svc.create_user(UserCreate(email="anonymous@system.local", password="anon", full_name="Anonymous", phone=None))
        return user
    except Exception:
        result = await db.execute(select(User).where(User.email == "anonymous@system.local"))
        return result.scalar_one()

@router.post("/requests", response_model=ServiceRequestResponse, dependencies=[Depends(limit_create)])
async def submit_request(request_create: ServiceRequestCreate, db: AsyncSession = Depends(get_db)):
    anon = await _get_anonymous_user(db)
    svc = RequestService(db)
    req = await svc.create_request(request_create, anon.id)
    return req

@router.get("/requests/{request_id}/status", dependencies=[Depends(limit_status)])
async def request_status(request_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"id": req.id, "status": req.status.value}
