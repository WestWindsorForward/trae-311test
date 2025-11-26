from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttachmentBase(BaseModel):
    description: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    request_id: int

class AttachmentInDB(AttachmentBase):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_scanned: int  # 0=pending, 1=clean, 2=infected
    scan_result: Optional[str] = None
    request_id: int
    uploaded_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AttachmentResponse(AttachmentInDB):
    uploaded_by_name: Optional[str] = None

class AttachmentUploadResponse(BaseModel):
    message: str
    attachment: AttachmentResponse