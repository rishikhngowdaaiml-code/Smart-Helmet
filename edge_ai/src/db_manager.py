import sqlite3
import os
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_path="database/violations.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
        
    def get_connection(self):
        # Enable sqlite3 thread support by using check_same_thread=False
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Module 3 - Database Schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT,
                    violation_type TEXT,
                    timestamp DATETIME,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    image_path TEXT,
                    video_path TEXT,
                    device_id TEXT,
                    detection_confidence REAL,
                    ocr_confidence REAL
                )
            ''')
            # Create an index to dramatically speed up duplicate lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_plate_time 
                ON violations(plate_number, timestamp)
            ''')
            conn.commit()

    def get_latest_capture_time(self, plate_number):
        """Returns the datetime of the latest violation for a given plate, or None."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp FROM violations 
                WHERE plate_number = ? 
                ORDER BY timestamp DESC LIMIT 1
            ''', (plate_number,))
            row = cursor.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
            return None

    def insert_violation(self, record):
        """
        Inserts a new violation record into the SQLite database.
        Returns the inserted violation_id.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO violations (
                    plate_number, violation_type, timestamp, gps_latitude, 
                    gps_longitude, image_path, video_path, device_id, 
                    detection_confidence, ocr_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('plate_number', 'UNKNOWN'),
                record.get('type', 'Unknown'),
                record.get('timestamp', datetime.now().isoformat()),
                record.get('gps_latitude', 0.0),
                record.get('gps_longitude', 0.0),
                record.get('image_path', ''),
                record.get('video_path', ''),
                record.get('device_id', 'HELMET-001'),
                record.get('detection_confidence', 1.0),
                record.get('ocr_confidence', 1.0)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_violations(self):
        """Returns all violations as a list of dictionaries (used by API)."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM violations ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
