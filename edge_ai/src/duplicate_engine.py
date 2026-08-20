import yaml
import logging
from datetime import datetime, timedelta
import os
from thefuzz import fuzz

class DuplicateEngine:
    def __init__(self, db_manager, config_path="../config.yaml"):
        self.db = db_manager
        self.config = self._load_config(config_path)
        
        # Module 8 - Logging Setup
        self.logger = logging.getLogger("DuplicateEngine")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            
    def _load_config(self, config_path):
        default_config = {
            "duplicate_cooldown_minutes": 60,
            "ocr_confidence_threshold": 0.90,
            "fuzzy_match_threshold": 0.95,
            "evidence_buffer_seconds": 10
        }
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return {**default_config, **(config or {})}
        except Exception as e:
            print(f"Failed to load config: {e}. Using defaults.")
        return default_config

    def normalize_plate(self, plate_text):
        """Module 4: Normalizes common OCR confusions"""
        if not plate_text:
            return ""
        # Remove whitespace and special characters, force uppercase
        normalized = ''.join(e for e in plate_text if e.isalnum()).upper()
        
        # Example Indian plate confusion mapping
        # Only swap O/0 if we can infer context (e.g. first two are letters, next two are numbers)
        # For simplicity, we just do basic string cleanup here as Regex handles validation later.
        return normalized

    def is_duplicate(self, plate_number):
        """
        Module 2 - Duplicate Detection Engine
        Checks if the plate was seen recently (within cooldown).
        """
        normalized_plate = self.normalize_plate(plate_number)
        
        # Never block if plate is empty or UNKNOWN
        if not normalized_plate or normalized_plate == "UNKNOWN":
            return False
            
        cooldown_minutes = self.config.get("duplicate_cooldown_minutes", 1)
        
        # Query DB for the exact plate
        last_time = self.db.get_latest_capture_time(normalized_plate)
        
        if last_time:
            elapsed = datetime.now() - last_time
            if elapsed < timedelta(minutes=cooldown_minutes):
                self.logger.info(f"Duplicate ignored for {normalized_plate}. Last seen {elapsed.total_seconds()/60:.1f} mins ago.")
                return True
                
        # Module 4: Fuzzy Matching for OCR errors
        # (e.g. "KA01AB1234" vs "KA01AB123A")
        # We fetch recent records and compare using Levenshtein distance
        recent_records = self.db.get_all_violations() # In a real scale system, limit to last 24h
        
        threshold = self.config.get("fuzzy_match_threshold", 0.95) * 100
        
        for record in recent_records:
            record_time = datetime.fromisoformat(record['timestamp'])
            elapsed = datetime.now() - record_time
            
            if elapsed < timedelta(minutes=cooldown_minutes):
                score = fuzz.ratio(normalized_plate, record['plate_number'])
                if score >= threshold:
                    self.logger.info(f"Fuzzy duplicate ignored! {normalized_plate} matched {record['plate_number']} with {score}% confidence.")
                    return True

        self.logger.info(f"New violation captured for {normalized_plate}!")
        return False
