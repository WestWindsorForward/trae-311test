from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class RequestStatus(enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CLOSED = "closed"

class RequestPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

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