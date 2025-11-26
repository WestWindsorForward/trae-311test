from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.request import RequestStatus, RequestPriority, RequestCategory

class ServiceRequestBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: RequestCategory
    priority: RequestPriority = RequestPriority.MEDIUM
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = Field(None, max_length=500)
    is_anonymous: bool = False

class ServiceRequestCreate(ServiceRequestBase):
    pass

class ServiceRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[RequestCategory] = None
    priority: Optional[RequestPriority] = None
    status: Optional[RequestStatus] = None
    assigned_staff_id: Optional[int] = None
    estimated_completion_date: Optional[datetime] = None

class ServiceRequestInDB(ServiceRequestBase):
    id: int
    status: RequestStatus
    citizen_id: int
    assigned_staff_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class ServiceRequestResponse(ServiceRequestInDB):
    citizen_name: Optional[str] = None
    assigned_staff_name: Optional[str] = None
    attachment_count: int = 0
    comment_count: int = 0

class ServiceRequestList(BaseModel):
    items: List[ServiceRequestResponse]
    total: int
    page: int
    size: int
    pages: int

class ServiceRequestFilter(BaseModel):
    status: Optional[RequestStatus] = None
    category: Optional[RequestCategory] = None
    priority: Optional[RequestPriority] = None
    citizen_id: Optional[int] = None
    assigned_staff_id: Optional[int] = None
    search: Optional[str] = None