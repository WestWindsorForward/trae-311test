from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..api.dependencies import get_current_active_user, get_staff_user
from ..services.request_service import RequestService
from ..services.attachment_service import AttachmentService
from ..services.comment_service import CommentService
from ..schemas.request import (
    ServiceRequestCreate, 
    ServiceRequestUpdate, 
    ServiceRequestResponse, 
    ServiceRequestList,
    ServiceRequestFilter
)
from ..schemas.attachment import AttachmentResponse
from ..schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from ..models.user import User, UserRole
from ..models.request import RequestStatus, RequestCategory, RequestPriority

router = APIRouter(prefix="/requests", tags=["service-requests"])

@router.post("/", response_model=ServiceRequestResponse)
async def create_request(
    request_create: ServiceRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new service request"""
    request_service = RequestService(db)
    try:
        request = await request_service.create_request(request_create, current_user.id)
        return request
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=ServiceRequestList)
async def get_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[RequestStatus] = None,
    category: Optional[RequestCategory] = None,
    priority: Optional[RequestPriority] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of service requests with filtering"""
    request_service = RequestService(db)
    
    # Build filter
    filter_params = ServiceRequestFilter(
        status=status,
        category=category,
        priority=priority,
        search=search
    )
    
    # Apply role-based filtering
    user_id = current_user.id if current_user.role == UserRole.CITIZEN else None
    user_role = current_user.role.value
    
    requests, total = await request_service.get_requests_list(
        skip=skip,
        limit=limit,
        filter_params=filter_params,
        user_id=user_id,
        user_role=user_role
    )
    
    return ServiceRequestList(
        items=requests,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{request_id}", response_model=ServiceRequestResponse)
async def get_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific service request"""
    request_service = RequestService(db)
    request = await request_service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CITIZEN and request.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request"
        )
    
    return request

@router.put("/{request_id}", response_model=ServiceRequestResponse)
async def update_request(
    request_id: int,
    request_update: ServiceRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Update a service request (staff only)"""
    request_service = RequestService(db)
    request = await request_service.update_request(request_id, request_update, current_user.id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return request

@router.post("/{request_id}/assign", response_model=ServiceRequestResponse)
async def assign_request(
    request_id: int,
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Assign a request to staff member"""
    request_service = RequestService(db)
    request = await request_service.assign_request(request_id, staff_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return request

@router.post("/{request_id}/status", response_model=ServiceRequestResponse)
async def update_request_status(
    request_id: int,
    status: RequestStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Update request status"""
    request_service = RequestService(db)
    request = await request_service.update_request_status(request_id, status, current_user.id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return request

# Attachment endpoints
@router.post("/{request_id}/attachments", response_model=AttachmentResponse)
async def upload_attachment(
    request_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload an attachment to a request"""
    # Check if request exists and user has access
    request_service = RequestService(db)
    request = await request_service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CITIZEN and request.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add attachments to this request"
        )
    
    attachment_service = AttachmentService(db)
    try:
        attachment = await attachment_service.save_uploadfile(
            upload=file,
            request_id=request_id,
            uploaded_by_id=current_user.id,
            description=description
        )
        return attachment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{request_id}/attachments", response_model=List[AttachmentResponse])
async def get_attachments(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attachments for a request"""
    # Check if request exists and user has access
    request_service = RequestService(db)
    request = await request_service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CITIZEN and request.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view attachments for this request"
        )
    
    attachment_service = AttachmentService(db)
    attachments = await attachment_service.get_attachments_by_request(request_id)
    return attachments

# Comment endpoints
@router.post("/{request_id}/comments", response_model=CommentResponse)
async def create_comment(
    request_id: int,
    comment_create: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a comment on a request"""
    # Check if request exists and user has access
    request_service = RequestService(db)
    request = await request_service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CITIZEN and request.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to comment on this request"
        )
    
    comment_service = CommentService(db)
    comment = await comment_service.create_comment(comment_create, current_user.id)
    return comment

@router.get("/{request_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    request_id: int,
    include_internal: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comments for a request"""
    # Check if request exists and user has access
    request_service = RequestService(db)
    request = await request_service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CITIZEN and request.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view comments for this request"
        )
    
    # Only staff can see internal comments
    if current_user.role == UserRole.CITIZEN:
        include_internal = False
    
    comment_service = CommentService(db)
    comments = await comment_service.get_comments_by_request(
        request_id, include_internal, skip, limit
    )
    return comments
