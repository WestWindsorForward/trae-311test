from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..api.dependencies import get_admin_user
from ..models.models import GeoBoundary, ApiCredential
from ..core.crypto import get_fernet

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/geo-boundaries")
async def upload_boundary(name: str, geojson: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    boundary = GeoBoundary(name=name, geojson=geojson)
    db.add(boundary)
    await db.commit()
    await db.refresh(boundary)
    return {"id": boundary.id, "name": boundary.name}

@router.get("/geo-boundaries")
async def list_boundaries(db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    result = await db.execute(select(GeoBoundary))
    items = result.scalars().all()
    return [{"id": b.id, "name": b.name} for b in items]

@router.post("/credentials")
async def set_credential(service_name: str, secret_value: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    f = get_fernet()
    enc = f.encrypt(secret_value.encode()).decode()
    result = await db.execute(select(ApiCredential).where(ApiCredential.service_name == service_name))
    existing = result.scalar_one_or_none()
    if existing:
        existing.encrypted_value = enc
        await db.commit()
        return {"service_name": existing.service_name}
    cred = ApiCredential(service_name=service_name, encrypted_value=enc, created_by_id=current_user.id)
    db.add(cred)
    await db.commit()
    await db.refresh(cred)
    return {"service_name": cred.service_name}

@router.get("/credentials")
async def list_credentials(db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    result = await db.execute(select(ApiCredential))
    items = result.scalars().all()
    return [{"service_name": c.service_name, "created_at": c.created_at.isoformat()} for c in items]
