from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from ..models.models import Comment, ServiceRequest
from ..schemas.comment import CommentCreate, CommentUpdate

class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_comment(self, comment_create: CommentCreate, author_id: int) -> Comment:
        # Validate request exists
        request_result = await self.db.execute(
            select(ServiceRequest).where(ServiceRequest.id == comment_create.request_id)
        )
        if not request_result.scalar_one_or_none():
            raise ValueError("Request not found")
        
        comment = Comment(
            **comment_create.dict(),
            author_id=author_id
        )
        
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment
    
    async def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        result = await self.db.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_comments_by_request(
        self, 
        request_id: int, 
        include_internal: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[Comment]:
        
        query = select(Comment).where(Comment.request_id == request_id)
        
        # Filter internal comments if not staff/admin
        if not include_internal:
            query = query.where(Comment.is_internal == False)
        
        query = query.order_by(desc(Comment.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_comment(self, comment_id: int, comment_update: CommentUpdate, author_id: int) -> Optional[Comment]:
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            return None
        
        # Check if user is the author
        if comment.author_id != author_id:
            raise ValueError("Not authorized to edit this comment")
        
        comment.content = comment_update.content
        await self.db.commit()
        await self.db.refresh(comment)
        return comment
    
    async def delete_comment(self, comment_id: int, author_id: int) -> bool:
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            return False
        
        # Check if user is the author
        if comment.author_id != author_id:
            raise ValueError("Not authorized to delete this comment")
        
        await self.db.delete(comment)
        await self.db.commit()
        return True