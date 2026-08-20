from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class EvidenceSchema(BaseModel):
    file_type: str
    file_path: Optional[str] = None
    metadata_json: Optional[Any] = None

class ViolationCreate(BaseModel):
    device_uid: str
    violation_type: str
    confidence_score: float
    location_lat: float
    location_lon: float
    violation_timestamp: datetime
    license_plate: Optional[str] = None
    evidence: List[EvidenceSchema] = []

class ViolationResponse(BaseModel):
    id: int
    violation_type: str
    confidence_score: float
    location_lat: float
    location_lon: float
    violation_timestamp: datetime
    
    class Config:
        from_attributes = True
