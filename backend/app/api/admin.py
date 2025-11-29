from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..api.dependencies import get_admin_user
from ..models.models import GeoBoundary, ApiCredential, Department, Jurisdiction, User, UserRole
from ..core.crypto import get_fernet
from ..services.department_service import DepartmentService
from ..services.jurisdiction_service import JurisdictionService
from pathlib import Path

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

@router.post("/update-now")
async def request_update(db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    # Signal host watcher to update and rebuild
    flag_dir = Path("/app/flags")
    flag_dir.mkdir(parents=True, exist_ok=True)
    (flag_dir / "update_requested").write_text("1")
    return {"ok": True}

@router.post("/departments")
async def create_department(payload: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    name = payload.get("name")
    code = payload.get("code")
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    dep = await DepartmentService(db).create(name, code)
    return {"id": dep.id, "name": dep.name, "code": dep.code}

@router.get("/departments")
async def list_departments(db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    items = await DepartmentService(db).list()
    return [{"id": d.id, "name": d.name, "code": d.code} for d in items]

@router.delete("/departments/{dep_id}")
async def delete_department(dep_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    await DepartmentService(db).delete(dep_id)
    return {"ok": True}

@router.post("/departments/{dep_id}/members")
async def update_department_members(dep_id: int, payload: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    user_id = int(payload.get("user_id"))
    action = payload.get("action")
    svc = DepartmentService(db)
    if action == "add":
        await svc.add_member(dep_id, user_id)
    elif action == "remove":
        await svc.remove_member(dep_id, user_id)
    else:
        raise HTTPException(status_code=400, detail="invalid action")
    return {"ok": True}

@router.post("/users/{user_id}/role")
async def set_user_role(user_id: int, role: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    try:
        user.role = UserRole(role)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid role")
    await db.commit()
    return {"id": user.id, "role": user.role.value}

@router.post("/jurisdictions")
async def create_jurisdiction(payload: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    name = payload.get("name")
    geojson = payload.get("geojson")
    active = bool(payload.get("active", True))
    if not name or not geojson:
        raise HTTPException(status_code=400, detail="name and geojson required")
    j = await JurisdictionService(db).create(name, geojson, active)
    return {"id": j.id, "name": j.name, "active": j.active}

@router.get("/jurisdictions")
async def list_jurisdictions(db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    items = await JurisdictionService(db).list()
    return [{"id": i.id, "name": i.name, "active": i.active} for i in items]

@router.put("/jurisdictions/{jid}")
async def update_jurisdiction(jid: int, payload: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    j = await JurisdictionService(db).update(jid, payload.get("name"), payload.get("geojson"), payload.get("active"))
    if not j:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": j.id, "name": j.name, "active": j.active}

@router.delete("/jurisdictions/{jid}")
async def delete_jurisdiction(jid: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_admin_user)):
    ok = await JurisdictionService(db).delete(jid)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}
