import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.main import send_automated_email

def run_verification():
    print("Verifying Automated Email System...")
    
    # Load DB to find TN 10 F 8325
    with open('violations_db.json', 'r') as f:
        db = json.load(f)
        
    target_record = None
    for record in db:
        if record['plate'] == 'TN 10 F 8325':
            target_record = record
            break
            
    if not target_record:
        print("Could not find record for TN 10 F 8325!")
        return
        
    snapshot_path = os.path.join('snapshots', f"{target_record['id']}.jpg")
    print(f"Found Record: {target_record}")
    print(f"Snapshot Path: {snapshot_path}")
    
    # Trigger Email
    send_automated_email(target_record, snapshot_path)

if __name__ == '__main__':
    run_verification()
