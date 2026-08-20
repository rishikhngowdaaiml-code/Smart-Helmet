import cv2
import numpy as np
import os
import collections
os.environ["FLAGS_use_mkldnn"] = "0"
from paddleocr import PaddleOCR
import re

class LicensePlateReader:
    def __init__(self):
        # We don't initialize PaddleOCR here anymore to avoid GIL deadlocks on Windows!
        # It will be lazy-loaded only when the first violation is detected.
        self.ocr = None
        
        # Strict Regex for Indian License Plates (e.g., KA01AB1234)
        # Matches formats like: MH 12 AB 1234, KA01AB1234, HR 26 BR 9012, etc.
        self.plate_pattern = re.compile(r'^[A-Z]{2}\s?[0-9]{1,2}\s?[A-Z]{1,2}\s?[0-9]{4}$')
        
        # Mapping for common OCR errors (Module 4)
        self.char_map = {
            'O': '0', 'Q': '0', 'I': '1', 'L': '1', 'Z': '2', 'S': '5', 'G': '6', 'B': '8'
        }
        self.fusion_buffer = collections.deque(maxlen=3)

    def _init_model(self):
        if self.ocr is None:
            print("🚀 Lazy-loading PaddleOCR C++ Backend for the first time...")
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', enable_mkldnn=False)
            print("✅ PaddleOCR Backend Initialized!")

    def enhance_for_ocr(self, image):
        """
        Module 8 - OCR Enhancement
        Applies Unsharp Masking (Module 5), Bilateral Filtering, and CLAHE to improve text contrast.
        """
        if image is None or image.size == 0:
            return image
            
        # 1. Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Upscale (Super Resolution for small plates)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # 3. Denoising / Bilateral Filter (preserves edges)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 4. Local Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(denoised)
        
        # 5. Adaptive Unsharp Masking (Module 5 - Motion Deblurring)
        gaussian = cv2.GaussianBlur(contrast, (9,9), 10.0)
        sharpened = cv2.addWeighted(contrast, 1.5, gaussian, -0.5, 0, contrast)
        
        # Convert back to BGR for PaddleOCR
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    def extract_text(self, plate_image):
        """Extract text using PaddleOCR"""
        if plate_image is None or plate_image.size == 0:
            return None
            
        # Module 4 & 5 & 8: Enhance Image
        enhanced_image = self.enhance_for_ocr(plate_image)
        
        # Lazy load PaddleOCR on the very first inference to avoid Windows C++ Thread Deadlocks!
        self._init_model()
        
        # We need an RGB image for PaddleOCR
        rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB)
        
        try:
            result = self.ocr.ocr(rgb_image, cls=True)
        except Exception as e:
            print(f"OCR Error: {e}")
            return None, 0.0
            
        if not result or not result[0]:
            return None, 0.0
        extracted_texts = []
        highest_confidence = 0.0
        
        for line in result[0]:
            try:
                # PaddleOCR result structure: [ [[x,y]...], (text, confidence) ]
                text = str(line[1][0])
                confidence = float(line[1][1])
                
                # Basic Normalization
                text = ''.join(e for e in text if e.isalnum()).upper()
                extracted_texts.append(text)
                if confidence > highest_confidence:
                    highest_confidence = confidence
            except Exception as e:
                continue
            
        combined_text = "".join(extracted_texts)
        if self.plate_pattern.match(combined_text):
            return combined_text, highest_confidence
            
        return combined_text if len(combined_text) > 4 else None, highest_confidence
