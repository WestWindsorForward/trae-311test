from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from datetime import datetime
from ..models.models import ServiceRequest, RequestStatus, RequestPriority, RequestCategory, User
from ..schemas.request import ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestFilter
from .audit_service import AuditService
from .gis import is_point_in_boundary

class RequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_request(self, request_create: ServiceRequestCreate, citizen_id: int) -> ServiceRequest:
        ok = await is_point_in_boundary(self.db, request_create.latitude, request_create.longitude)
        if not ok:
            raise ValueError("Location outside township boundary")
        request = ServiceRequest(
            **request_create.dict(),
            citizen_id=citizen_id,
            status=RequestStatus.SUBMITTED
        )
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request
    
    async def get_request_by_id(self, request_id: int) -> Optional[ServiceRequest]:
        result = await self.db.execute(
            select(ServiceRequest)
            .where(ServiceRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def get_request_with_relations(self, request_id: int) -> Optional[ServiceRequest]:
        result = await self.db.execute(
            select(ServiceRequest)
            .join(User, ServiceRequest.citizen_id == User.id)
            .where(ServiceRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def update_request(self, request_id: int, request_update: ServiceRequestUpdate, updated_by_id: int) -> Optional[ServiceRequest]:
        request = await self.get_request_by_id(request_id)
        if not request:
            return None
        
        update_data = request_update.dict(exclude_unset=True)
        
        # Set completion date if status is changed to completed
        if "status" in update_data and update_data["status"] == RequestStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(request, field, value)
        
        request.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(request)
        await AuditService(self.db).log(updated_by_id, "update_request", "ServiceRequest", request.id, request_update.dict(exclude_unset=True))
        return request
    
    async def get_requests_list(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filter_params: Optional[ServiceRequestFilter] = None,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None
    ) -> tuple[List[ServiceRequest], int]:
        
        query = select(ServiceRequest).join(User, ServiceRequest.citizen_id == User.id)
        
        # Apply filters
        if filter_params:
            if filter_params.status:
                query = query.where(ServiceRequest.status == filter_params.status)
            if filter_params.category:
                query = query.where(ServiceRequest.category == filter_params.category)
            if filter_params.priority:
                query = query.where(ServiceRequest.priority == filter_params.priority)
            if filter_params.citizen_id:
                query = query.where(ServiceRequest.citizen_id == filter_params.citizen_id)
            if filter_params.assigned_staff_id:
                query = query.where(ServiceRequest.assigned_staff_id == filter_params.assigned_staff_id)
            if filter_params.search:
                search_term = f"%{filter_params.search}%"
                query = query.where(
                    or_(
                        ServiceRequest.title.ilike(search_term),
                        ServiceRequest.description.ilike(search_term),
                        User.full_name.ilike(search_term)
                    )
                )
        
        # Role-based filtering
        if user_role == "citizen":
            query = query.where(ServiceRequest.citizen_id == user_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        requests = result.scalars().all()
        
        return list(requests), total
    
    async def assign_request(self, request_id: int, staff_id: int) -> Optional[ServiceRequest]:
        updated = await self.update_request(
            request_id, 
            ServiceRequestUpdate(assigned_staff_id=staff_id, status=RequestStatus.ASSIGNED),
            staff_id
        )
        if updated:
            await AuditService(self.db).log(staff_id, "assign_request", "ServiceRequest", updated.id, {"assigned_staff_id": staff_id})
        return updated
    
    async def update_request_status(self, request_id: int, status: RequestStatus, updated_by_id: int) -> Optional[ServiceRequest]:
        updated = await self.update_request(
            request_id,
            ServiceRequestUpdate(status=status),
            updated_by_id
        )
        if updated:
            await AuditService(self.db).log(updated_by_id, "update_status", "ServiceRequest", updated.id, {"status": status.value})
        return updated
