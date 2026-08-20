import cv2
import numpy as np

class VideoStabilizer:
    def __init__(self, smoothing_radius=5, blur_threshold=100.0):
        # Smoothing radius determines how aggressively to smooth the camera motion.
        self.smoothing_radius = smoothing_radius
        # Threshold for variance of laplacian (blur detection)
        self.blur_threshold = blur_threshold
        
        # State variables for stabilization
        self.prev_gray = None
        self.transforms = []
        self.frame_buffer = []
        self.max_buffer_size = 5 # Temporal window for adaptive frame selection
        
    def detect_blur(self, frame):
        """
        Module 2 - Blur Detection
        Calculates the Variance of Laplacian to score image sharpness.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = blur_score < self.blur_threshold
        return blur_score, is_blurry

    def stabilize(self, frame):
        """
        Module 1 - Video Stabilization
        Uses Optical Flow (Lucas-Kanade) to track features and correct camera shake.
        """
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray is None:
            self.prev_gray = curr_gray
            # Initialize with no transform
            self.transforms.append([0, 0, 0])
            return frame
            
        # Detect features in previous frame
        prev_pts = cv2.goodFeaturesToTrack(self.prev_gray,
                                         maxCorners=200,
                                         qualityLevel=0.01,
                                         minDistance=30,
                                         blockSize=3)
        
        if prev_pts is None or len(prev_pts) < 5:
            self.prev_gray = curr_gray
            return frame # Can't stabilize without features
            
        # Track features to current frame
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, curr_gray, prev_pts, None)
        
        # Filter valid points
        idx = np.where(status==1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]
        
        if len(prev_pts) < 5:
            self.prev_gray = curr_gray
            return frame
            
        # Find rigid transformation (translation + rotation)
        # Using partial affine to prevent shearing/scaling distortions from extreme vibrations
        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
        
        if m is None:
            self.prev_gray = curr_gray
            return frame
            
        # Extract translation and rotation
        dx = m[0, 2]
        dy = m[1, 2]
        da = np.arctan2(m[1, 0], m[0, 0])
        
        self.transforms.append([dx, dy, da])
        
        # Smooth transformations using a moving average
        smoothed_transforms = self._moving_average(self.transforms, self.smoothing_radius)
        
        # Calculate the difference between smoothed and actual transforms
        diff = smoothed_transforms[-1] - self.transforms[-1]
        
        # Create the affine transformation matrix to apply the correction
        dx, dy, da = diff
        m_correct = np.zeros((2,3), np.float32)
        m_correct[0,0] = np.cos(da)
        m_correct[0,1] = -np.sin(da)
        m_correct[1,0] = np.sin(da)
        m_correct[1,1] = np.cos(da)
        m_correct[0,2] = dx
        m_correct[1,2] = dy
        
        h, w = frame.shape[:2]
        # Warp the frame to stabilize
        stabilized_frame = cv2.warpAffine(frame, m_correct, (w,h))
        
        self.prev_gray = curr_gray
        return stabilized_frame

    def _moving_average(self, curve, radius):
        window_size = 2 * radius + 1
        f = np.ones(window_size) / window_size
        curve_pad = np.pad(curve, ((radius, radius), (0,0)), 'edge')
        curve_smoothed = np.zeros_like(curve)
        
        for i in range(3): # Smooth dx, dy, da
            curve_smoothed[:, i] = np.convolve(curve_pad[:, i], f, mode='same')[radius:-radius]
            
        return curve_smoothed

    def adaptive_frame_selection(self, frame):
        """
        Module 3 - Adaptive Frame Selection
        Buffers frames and returns the sharpest one from the recent temporal window.
        """
        blur_score, is_blurry = self.detect_blur(frame)
        self.frame_buffer.append((frame, blur_score))
        
        if len(self.frame_buffer) > self.max_buffer_size:
            self.frame_buffer.pop(0)
            
        # Return the frame with the maximum blur score (sharpest)
        best_frame, best_score = max(self.frame_buffer, key=lambda x: x[1])
        return best_frame, best_score, is_blurry
