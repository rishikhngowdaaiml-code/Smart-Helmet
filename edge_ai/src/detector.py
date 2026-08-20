from ultralytics import YOLO
import cv2
import math

class TrafficViolationDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # In a real scenario, this should be the custom trained model
        # We load a pretrained model for placeholder
        self.model = YOLO(model_path)
        
        # Assume class mapping for custom model: 0: helmet, 1: no_helmet, 2: person, 3: motorcycle
        # Using COCO mapping as placeholder for now, mapping Person(0) and Motorcycle(3)
        self.class_names = self.model.names

    def is_inside(self, inner_box, outer_box):
        """
        Check if a person (inner_box) is riding a motorcycle (outer_box).
        Uses horizontal alignment and vertical positioning rather than strict IoU,
        so people sitting far back on a bike are still correctly grouped!
        """
        px1, py1, px2, py2 = inner_box
        mx1, my1, mx2, my2 = outer_box
        
        # Calculate horizontal overlap
        overlap_w = max(0, min(px2, mx2) - max(px1, mx1))
        p_w = px2 - px1
        
        # If the person is at least 30% horizontally inside the motorcycle's X coordinates
        # AND the person is generally above or on the motorcycle
        if p_w > 0 and overlap_w / p_w > 0.3 and py1 < my2:
            return True
            
        return False

    def process_frame(self, frame):
        # Run inference with tracking
        results = self.model.track(frame, stream=True, verbose=False, persist=True, tracker="bytetrack.yaml")
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                b = box.xyxy[0].cpu().numpy().tolist()
                
                # Get ByteTrack ID if available
                obj_id = -1
                if box.id is not None:
                    obj_id = int(box.id[0])
                
                name = self.model.names[cls_id]
                detections.append({
                    "id": obj_id,
                    "bbox": b,
                    "conf": conf,
                    "class": cls_id,
                    "name": name
                })

        # Logic for Triple Riding and No Helmet
        violations = []
        
        motorcycles = [d for d in detections if (d["name"] == "motorcycle" or d["name"] == "3") and d["conf"] >= 0.60]
        people = [d for d in detections if (d["name"] == "person" or d["name"] == "0") and d["conf"] >= 0.45]
        
        # Draw bounding boxes
        annotated_frame = frame.copy()
        
        for mc in motorcycles:
            mc_box = mc["bbox"]
            
            # -------------------------------------------------------------
            # Distance / Proximity Filter
            # -------------------------------------------------------------
            # Only process motorcycles that are within ~2 meters of the camera.
            # This ensures the vehicle is large enough in the frame (640x480) 
            # for the number plate to be clearly visible and recognizable by OCR.
            mc_w = mc_box[2] - mc_box[0]
            mc_h = mc_box[3] - mc_box[1]
            if mc_w < 100 or mc_h < 100:
                # Motorcycle is too far away, skip violation detection to avoid bad OCR
                continue
                
            cv2.rectangle(annotated_frame, (int(mc_box[0]), int(mc_box[1])), (int(mc_box[2]), int(mc_box[3])), (255, 0, 0), 2)
            cv2.putText(annotated_frame, f"Motorcycle ID: {mc['id']}", (int(mc_box[0]), int(mc_box[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

            riders_on_mc = []
            for p in people:
                if self.is_inside(p["bbox"], mc_box):
                    riders_on_mc.append(p)

            # -------------------------------------------------------------
            # NEW: Custom Model Layer for Family / Child Recognition
            # -------------------------------------------------------------
            # We determine if this is a family (parent with kids) rather than true triple riding
            # by analyzing the spatial arrangement. Children usually sit in front of the driver 
            # (on the tank) or are sandwiched closely.
            
            is_family = False
            if len(riders_on_mc) > 2:
                # Find the main driver (usually the one furthest back but with the largest height)
                # or just use the largest bounding box
                largest_rider = max(riders_on_mc, key=lambda r: (r["bbox"][2]-r["bbox"][0])*(r["bbox"][3]-r["bbox"][1]))
                lx1, ly1, lx2, ly2 = largest_rider["bbox"]
                
                kids_detected = 0
                for rider in riders_on_mc:
                    if rider == largest_rider: continue
                    rx1, ry1, rx2, ry2 = rider["bbox"]
                    
                    # Pattern 1: Child on gas tank (sitting in front of adult)
                    # Bounding box is shifted forward and is much shorter or completely enclosed
                    if rx2 < lx2 and (ry2 - ry1) < (ly2 - ly1) * 0.85:
                        kids_detected += 1
                        
                    # Pattern 2: Sandwiched child
                    # High overlap with the adult's bounding box horizontally
                    overlap = max(0, min(rx2, lx2) - max(rx1, lx1))
                    if overlap / (rx2 - rx1) > 0.6 and (ry2 - ry1) < (ly2 - ly1) * 0.95:
                        kids_detected += 1
                        
                if kids_detected > 0:
                    is_family = True

            # Triple Riding Check: Only applies if it's NOT a family with kids
            if len(riders_on_mc) > 2 and not is_family:
                violations.append({
                    "type": "TRIPLE_RIDING",
                    "bbox": mc_box,
                    "conf": mc["conf"],
                    "rider_count": len(riders_on_mc)
                })

            # Helmet Violation Check for 2 persons
            if len(riders_on_mc) == 2 and not is_family:
                # Identify rider and pillion by bounding box area (driver is usually larger)
                riders_sorted = sorted(riders_on_mc, key=lambda r: (r["bbox"][2]-r["bbox"][0])*(r["bbox"][3]-r["bbox"][1]), reverse=True)
                rider = riders_sorted[0]
                pillion = riders_sorted[1]
                
                # Heuristic fake helmet detector: crops the top 20% of the person (the head)
                def has_helmet(r):
                    x1, y1, x2, y2 = map(int, r["bbox"])
                    head_y2 = y1 + int((y2 - y1) * 0.2)
                    if head_y2 <= y1 or x2 <= x1: return False
                    head_crop = frame[y1:head_y2, x1:x2]
                    if head_crop.size == 0: return False
                    hsv = cv2.cvtColor(head_crop, cv2.COLOR_BGR2HSV)
                    # Use a very strict threshold (e.g. pure white/bright colors) to avoid false positives on skin/hair
                    return hsv[:,:,2].mean() > 200 or hsv[:,:,1].mean() > 150

                rider_helmet = has_helmet(rider)
                pillion_helmet = has_helmet(pillion)
                
                violation_str = None
                if not rider_helmet and not pillion_helmet:
                    violation_str = "Rider and pillion rider both not wearing helmet"
                elif not rider_helmet and pillion_helmet:
                    violation_str = "Rider not wearing helmet"
                elif rider_helmet and not pillion_helmet:
                    violation_str = "Pillion rider not wearing helmet"
                    
                if violation_str:
                    # Draw red bounding boxes for violators
                    if not rider_helmet:
                        rx1, ry1, rx2, ry2 = map(int, rider["bbox"])
                        cv2.rectangle(annotated_frame, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)
                    if not pillion_helmet:
                        px1, py1, px2, py2 = map(int, pillion["bbox"])
                        cv2.rectangle(annotated_frame, (px1, py1), (px2, py2), (0, 0, 255), 2)
                        
                    violations.append({
                        "type": violation_str,
                        "bbox": rider["bbox"], # Assign the violation to the main rider's box for tracking
                        "conf": rider["conf"]
                    })
            elif len(riders_on_mc) == 1:
                rider = riders_on_mc[0]
                def has_helmet(r):
                    x1, y1, x2, y2 = map(int, r["bbox"])
                    head_y2 = y1 + int((y2 - y1) * 0.2)
                    if head_y2 <= y1 or x2 <= x1: return False
                    head_crop = frame[y1:head_y2, x1:x2]
                    if head_crop.size == 0: return False
                    hsv = cv2.cvtColor(head_crop, cv2.COLOR_BGR2HSV)
                    return hsv[:,:,2].mean() > 200 or hsv[:,:,1].mean() > 150
                    
                if not has_helmet(rider):
                    rx1, ry1, rx2, ry2 = map(int, rider["bbox"])
                    cv2.rectangle(annotated_frame, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)
                    violations.append({
                        "type": "Rider not wearing helmet",
                        "bbox": rider["bbox"],
                        "conf": rider["conf"]
                    })

        # Draw violations
        for v in violations:
            box = v["bbox"]
            cv2.putText(annotated_frame, f"VIOLATION: {v['type']}", (int(box[0]), int(box[1])-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        return annotated_frame, violations, detections
