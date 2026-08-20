import cv2

def test_cameras():
    print("Testing cameras...")
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera index {i} is WORKING! Resolution: {frame.shape}")
            else:
                print(f"Camera index {i} opened, but failed to read frame.")
            cap.release()
        else:
            print(f"Camera index {i} is NOT available.")

if __name__ == "__main__":
    test_cameras()
