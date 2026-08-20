import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json
import shutil

from app.db.database import get_db
from app.db import models
from app.api.schemas import ViolationCreate, ViolationResponse

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/violations/upload")
async def upload_violation(
    device_uid: str = Form(...),
    violation_type: str = Form(...),
    confidence_score: float = Form(...),
    location_lat: float = Form(...),
    location_lon: float = Form(...),
    violation_timestamp: str = Form(...),
    license_plate: str = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Get or create device
    device = db.query(models.Device).filter(models.Device.device_uid == device_uid).first()
    if not device:
        device = models.Device(device_uid=device_uid, description="Auto-registered")
        db.add(device)
        db.commit()
        db.refresh(device)
        
    # Get or create vehicle
    vehicle_id = None
    if license_plate:
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.license_plate == license_plate).first()
        if not vehicle:
            vehicle = models.Vehicle(license_plate=license_plate)
            db.add(vehicle)
            db.commit()
            db.refresh(vehicle)
        vehicle_id = vehicle.id

    # Create violation
    timestamp = datetime.fromisoformat(violation_timestamp.replace('Z', '+00:00'))
    violation = models.Violation(
        device_id=device.id,
        vehicle_id=vehicle_id,
        violation_type=violation_type,
        confidence_score=confidence_score,
        location_lat=location_lat,
        location_lon=location_lon,
        violation_timestamp=timestamp
    )
    db.add(violation)
    db.commit()
    db.refresh(violation)

    # Save files as evidence
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, f"{violation.id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_type = "IMAGE" if file.content_type.startswith("image/") else "VIDEO"
        evidence = models.Evidence(
            violation_id=violation.id,
            file_path=file_path,
            file_type=file_type
        )
        db.add(evidence)
    
    db.commit()
    
    # Optional: trigger email service here
    # send_violation_email(violation)

    return {"status": "success", "violation_id": violation.id}

@router.get("/violations", response_model=List[ViolationResponse])
def get_violations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    violations = db.query(models.Violation).order_by(models.Violation.violation_timestamp.desc()).offset(skip).limit(limit).all()
    return violations
