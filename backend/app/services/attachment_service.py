import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile
from aiofiles import open as aio_open
from ..models.models import Attachment, ServiceRequest
from ..core.config import settings
import clamd

class AttachmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path("/app/uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.clamav = None
    
    async def _get_clamav_connection(self):
        """Get ClamAV connection"""
        if not self.clamav:
            try:
                self.clamav = clamd.ClamdNetworkSocket(
                    host=settings.clamav_host,
                    port=settings.clamav_port
                )
            except Exception:
                self.clamav = None
        return self.clamav
    
    def _validate_file(self, filename: str, file_size: int) -> bool:
        """Validate file type and size"""
        if file_size > settings.max_file_size:
            return False
        
        file_extension = Path(filename).suffix.lower().lstrip('.')
        if file_extension not in settings.allowed_file_types:
            return False
        
        return True
    
    async def _scan_file(self, file_path: Path) -> tuple[int, Optional[str]]:
        """Scan file with ClamAV"""
        try:
            clamav = await self._get_clamav_connection()
            if not clamav:
                return 0, "Scanner unavailable"  # Mark as pending if scanner unavailable
            
            scan_result = clamav.scan(str(file_path))
            file_key = str(file_path)
            
            if file_key in scan_result:
                result = scan_result[file_key]
                if result[0] == "OK":
                    return 1, "Clean"  # Clean
                elif result[0] == "FOUND":
                    return 2, result[1]  # Infected
            
            return 0, "Scan failed"  # Pending
            
        except Exception as e:
            return 0, f"Scan error: {str(e)}"  # Pending on error
    
    async def save_attachment(
        self, 
        file_content: bytes, 
        original_filename: str, 
        request_id: int, 
        uploaded_by_id: int,
        description: Optional[str] = None
    ) -> Attachment:
        
        # Validate request exists
        request_result = await self.db.execute(
            select(ServiceRequest).where(ServiceRequest.id == request_id)
        )
        if not request_result.scalar_one_or_none():
            raise ValueError("Request not found")
        
        # Validate file
        file_size = len(file_content)
        if not self._validate_file(original_filename, file_size):
            raise ValueError("Invalid file type or size")
        
        # Generate unique filename
        file_extension = Path(original_filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Scan file
        is_scanned, scan_result = await self._scan_file(file_path)
        
        # Create attachment record
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            is_scanned=is_scanned,
            scan_result=scan_result,
            request_id=request_id,
            uploaded_by_id=uploaded_by_id
        )
        
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        
        return attachment

    async def save_uploadfile(
        self,
        upload: UploadFile,
        request_id: int,
        uploaded_by_id: int,
        description: Optional[str] = None
    ) -> Attachment:
        request_result = await self.db.execute(select(ServiceRequest).where(ServiceRequest.id == request_id))
        if not request_result.scalar_one_or_none():
            raise ValueError("Request not found")
        original_filename = upload.filename
        unique_filename = f"{uuid.uuid4()}{Path(original_filename).suffix}"
        file_path = self.upload_dir / unique_filename
        size = 0
        async with aio_open(file_path, "wb") as f:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                await f.write(chunk)
        if not self._validate_file(original_filename, size):
            file_path.unlink(missing_ok=True)
            raise ValueError("Invalid file type or size")
        mime_type, _ = mimetypes.guess_type(original_filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        is_scanned, scan_result = await self._scan_file(file_path)
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=str(file_path),
            file_size=size,
            mime_type=mime_type,
            description=description,
            is_scanned=is_scanned,
            scan_result=scan_result,
            request_id=request_id,
            uploaded_by_id=uploaded_by_id
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment
    
    async def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        result = await self.db.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_attachments_by_request(self, request_id: int) -> list[Attachment]:
        result = await self.db.execute(
            select(Attachment).where(Attachment.request_id == request_id)
        )
        return list(result.scalars().all())
    
    async def delete_attachment(self, attachment_id: int) -> bool:
        attachment = await self.get_attachment_by_id(attachment_id)
        if not attachment:
            return False
        
        # Delete physical file
        try:
            file_path = Path(attachment.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Don't fail if file deletion fails
        
        # Delete database record
        await self.db.delete(attachment)
        await self.db.commit()
        return True
