import requests
import os
import json

class BackendClient:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url

    def upload_violation(self, device_uid, violation_type, conf, lat, lon, timestamp, license_plate, image_path, video_path):
        url = f"{self.base_url}/violations/upload"
        
        data = {
            "device_uid": device_uid,
            "violation_type": violation_type,
            "confidence_score": str(conf),
            "location_lat": str(lat),
            "location_lon": str(lon),
            "violation_timestamp": timestamp,
        }
        
        if license_plate:
            data["license_plate"] = license_plate
            
        files = []
        if image_path and os.path.exists(image_path):
            files.append(("files", (os.path.basename(image_path), open(image_path, "rb"), "image/jpeg")))
        if video_path and os.path.exists(video_path):
            files.append(("files", (os.path.basename(video_path), open(video_path, "rb"), "video/mp4")))
            
        try:
            response = requests.post(url, data=data, files=files)
            print(f"Uploaded violation. Response: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"Failed to upload violation: {e}")
            return None
        finally:
            # Close files
            for _, file_tuple in files:
                file_tuple[1].close()
