from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Security
    is_scanned = Column(Integer, default=0)  # 0=pending, 1=clean, 2=infected
    scan_result = Column(String, nullable=True)
    
    # Relationships
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    request = relationship("ServiceRequest", backref="attachments")
    uploaded_by = relationship("User", backref="uploaded_attachments")