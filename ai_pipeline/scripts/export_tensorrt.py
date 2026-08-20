from ultralytics import YOLO

def export_model(model_path="runs/detect/smart_helmet_v1/weights/best.pt"):
    print(f"Loading model from {model_path}")
    model = YOLO(model_path)
    
    print("Exporting to ONNX format...")
    # Export to ONNX
    model.export(format="onnx", imgsz=640, simplify=True)
    
    print("Exporting to TensorRT format (requires TensorRT environment)...")
    # Export to TensorRT with FP16 precision
    try:
        model.export(format="engine", imgsz=640, half=True, workspace=4)
        print("Export completed successfully.")
    except Exception as e:
        print(f"Failed to export to TensorRT. Are you running on a Jetson/GPU with TensorRT installed? Error: {e}")

if __name__ == "__main__":
    export_model()
