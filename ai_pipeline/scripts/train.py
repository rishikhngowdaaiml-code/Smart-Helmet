from ultralytics import YOLO
import os

def train_model():
    print("Initializing YOLOv8 training pipeline...")
    
    # Load a pretrained model
    model = YOLO("yolov8m.pt")
    
    dataset_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/dataset.yaml"))
    
    # Train the model
    results = model.train(
        data=dataset_yaml,
        epochs=100,
        imgsz=640,
        batch=16,
        name="smart_helmet_v1",
        device="0", # GPU 0
        optimizer="auto",
        patience=20,
        save_period=10
    )
    
    print("Training completed. Validating...")
    # Validate the model
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map}")
    print(f"mAP50: {metrics.box.map50}")

if __name__ == "__main__":
    train_model()
