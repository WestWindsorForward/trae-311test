from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    is_internal: bool = False

class CommentCreate(CommentBase):
    request_id: int

class CommentUpdate(BaseModel):
    content: str

class CommentInDB(CommentBase):
    id: int
    request_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CommentResponse(CommentInDB):
    author_name: Optional[str] = None
    author_role: Optional[str] = None