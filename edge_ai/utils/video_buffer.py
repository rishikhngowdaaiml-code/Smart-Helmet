import collections
import cv2
import threading
import time
import os

class VideoBuffer:
    def __init__(self, fps=30, duration_seconds=10):
        self.fps = fps
        self.max_frames = fps * duration_seconds
        self.buffer = collections.deque(maxlen=self.max_frames)
        self.lock = threading.Lock()

    def add_frame(self, frame):
        with self.lock:
            self.buffer.append(frame.copy())

    def save_clip(self, output_path):
        with self.lock:
            frames_to_save = list(self.buffer)
            
        if not frames_to_save:
            return False

        height, width, layers = frames_to_save[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
        
        for frame in frames_to_save:
            out.write(frame)
            
        out.release()
        return True
