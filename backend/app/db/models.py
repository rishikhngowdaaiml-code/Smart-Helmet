from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_uid = Column(String(50), unique=True, nullable=False)
    description = Column(String)
    last_active = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    owner_info = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    violation_type = Column(String(50), nullable=False)
    confidence_score = Column(Float)
    location_lat = Column(Float)
    location_lon = Column(Float)
    violation_timestamp = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    device = relationship("Device")
    vehicle = relationship("Vehicle")
    evidence = relationship("Evidence", back_populates="violation")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id", ondelete="CASCADE"))
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    metadata_json = Column("metadata", JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

    violation = relationship("Violation", back_populates="evidence")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"))
    status = Column(String(20), default="PENDING")
    email_sent_to = Column(String(100))
    sent_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
