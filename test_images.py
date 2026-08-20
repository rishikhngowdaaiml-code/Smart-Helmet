import cv2
import sys
import os
import json
import threading
from datetime import datetime

sys.path.append('edge_ai/src')
from detector import TrafficViolationDetector
from plate_reader import LicensePlateReader
import main

det = TrafficViolationDetector('edge_ai/yolov8n.pt')
plate_reader = LicensePlateReader()

images = [
    r'C:\Users\1185r\.gemini\antigravity-ide\brain\449b1afe-797f-4ca6-8320-4b94b90fb10a\media__1782463485424.jpg'
]

os.makedirs('edge_ai/snapshots', exist_ok=True)
db_file = 'edge_ai/violations_db.json'
if os.path.exists(db_file):
    with open(db_file, 'r') as f:
        db = json.load(f)
else:
    db = []

for i, img_path in enumerate(images):
    print(f'\n--- Processing Test Image {i+3} ---')
    img = cv2.imread(img_path)
    if img is None: continue
    
    annotated_frame, violations, detections = det.process_frame(img)
    print("Detections:", detections)
    print("Violations:", violations)
    
    if violations:
        v = violations[0]
        box = v["bbox"]
        mc_crop = img[max(0, int(box[1])):int(box[3]), max(0, int(box[0])):int(box[2])]
        plate_text = plate_reader.extract_text(mc_crop)
        
        new_record = {
            'id': len(db) + 1,
            'type': v['type'],
            'plate': plate_text if plate_text else 'UNREADABLE',
            'time': datetime.now().strftime('%I:%M %p'),
            'conf': f"{int(v['conf']*100)}%",
            'location': 'Test Image Analysis',
            'status': 'Pending'
        }
        db.append(new_record)
        
        snapshot_path = os.path.join('edge_ai/snapshots', f"{new_record['id']}.jpg")
        
        # Geotag overlay logic
        snapshot_frame = img.copy()
        overlay = snapshot_frame.copy()
        h_img, w_img, _ = snapshot_frame.shape
        
        rect_h = 130
        cv2.rectangle(overlay, (0, h_img - rect_h), (w_img, h_img), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, snapshot_frame, 0.4, 0, snapshot_frame)
        
        now = datetime.now()
        date_str = now.strftime("%A, %d/%m/%Y %I:%M %p GMT +05:30")
        lat_lng = "Lat 12.921686° Long 77.542179°"
        location_details = "22, 21st Cross Rd, Ittamadu, Banashankari 3rd Stage, Banashankari, Bengaluru, Karnataka 560085, India"
        city_state = "Bengaluru, Karnataka, India"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(snapshot_frame, city_state, (20, h_img - 95), font, 0.8, (255, 255, 255), 2)
        cv2.putText(snapshot_frame, location_details, (20, h_img - 65), font, 0.5, (230, 230, 230), 1)
        cv2.putText(snapshot_frame, lat_lng, (20, h_img - 40), font, 0.5, (230, 230, 230), 1)
        cv2.putText(snapshot_frame, date_str, (20, h_img - 15), font, 0.5, (230, 230, 230), 1)
        
        cv2.imwrite(snapshot_path, snapshot_frame)
        
        print(f"🚨 ALERT: Logged {v['type']} | Plate: {new_record['plate']}")
        main.send_automated_email(new_record, snapshot_path)

with open(db_file, 'w') as f:
    json.dump(db, f, indent=2)
