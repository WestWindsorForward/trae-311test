from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# User Role Enum
class UserRole(enum.Enum):
    CITIZEN = "citizen"
    STAFF = "staff"
    ADMIN = "admin"

# Request Status Enum
class RequestStatus(enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CLOSED = "closed"

# Request Priority Enum
class RequestPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Request Category Enum
class RequestCategory(enum.Enum):
    ROAD_MAINTENANCE = "road_maintenance"
    STREET_LIGHTING = "street_lighting"
    TRAFFIC_SIGNALS = "traffic_signals"
    PARK_MAINTENANCE = "park_maintenance"
    WASTE_MANAGEMENT = "waste_management"
    WATER_SEWER = "water_sewer"
    NOISE_COMPLAINT = "noise_complaint"
    PARKING_ISSUE = "parking_issue"
    OTHER = "other"

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Service Request Model
class ServiceRequest(Base):
    __tablename__ = "service_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(RequestCategory), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.SUBMITTED, nullable=False)
    priority = Column(SQLEnum(RequestPriority), default=RequestPriority.MEDIUM, nullable=False)
    
    # Location information
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    
    # Relationships
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional fields
    is_anonymous = Column(Boolean, default=False)
    estimated_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    citizen = relationship("User", foreign_keys=[citizen_id], backref="submitted_requests")
    assigned_staff = relationship("User", foreign_keys=[assigned_staff_id], backref="assigned_requests")

# Attachment Model
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

# Comment Model
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal staff notes vs public comments
    
    # Relationships
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    request = relationship("ServiceRequest", backref="comments")
    author = relationship("User", backref="comments")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    actor = relationship("User")

class GeoBoundary(Base):
    __tablename__ = "geo_boundaries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geojson = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApiCredential(Base):
    __tablename__ = "api_credentials"
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, nullable=False)
    encrypted_value = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = relationship("User")
