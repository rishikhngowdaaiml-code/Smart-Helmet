from ultralytics import YOLO

# Module 10: Edge Optimization Utils
# Run this script on your target edge device (e.g. Jetson Nano)
# to export the PyTorch model to TensorRT for maximum inference speed.

def optimize_for_edge(model_path="yolov8n.pt", target_format="engine"):
    print(f"Loading base YOLOv8 model from {model_path}...")
    model = YOLO(model_path)
    
    print(f"Exporting model to {target_format} format...")
    if target_format == "engine":
        # Export to TensorRT (Requires TensorRT installed on device)
        # Use FP16 for massive speedups on NVIDIA edge devices with minimal accuracy loss
        model.export(format="engine", half=True, workspace=4, dynamic=True)
    elif target_format == "onnx":
        # Export to ONNX (More portable, still faster than native PyTorch)
        model.export(format="onnx", half=True)
        
    print(f"Export complete! Ensure detector.py is updated to load the new .{target_format} model file.")

if __name__ == "__main__":
    # If running on Jetson Orin Nano, 'engine' (TensorRT) is the best format.
    # If running on CPU or standard laptop GPU, 'onnx' might be easier to deploy.
    optimize_for_edge("yolov8n.pt", target_format="engine")
