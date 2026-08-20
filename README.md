# Edge AI Smart Helmet - Traffic Violation Detection System

An intelligent helmet-mounted surveillance and traffic safety system that uses Edge AI to automatically detect helmet violations, triple riding, and vehicle license plates with evidence-based reporting.

## 🌟 Key Features

* **Real-time Video Processing**: Capture streams at 720p/1080p using an Edge device (Jetson, Raspberry Pi).
* **Traffic Violation Detection**: YOLOv8-based model to detect People, Motorcycles, and Helmets.
* **Triple Riding Detection**: Custom IoU overlapping algorithm to group riders and flag >2 people on a single motorcycle.
* **License Plate OCR**: WPOD-NET (deskewing) + PaddleOCR for accurate Indian license plate detection.
* **Evidence Capture**: RAM-based circular buffer caches the last 10 seconds of video to only save evidence when a violation is triggered.
* **Automated Reporting**: FastAPI backend receives evidence, tags GPS coordinates via EXIF, and triggers SendGrid email alerts.
* **Modern Dashboard**: React + Vite UI with a glassmorphism design, live-feed placeholder, and analytics.

## 📂 Project Structure

```text
smart_helmet/
├── edge_ai/                    # Edge inference (YOLO, OCR, Buffer)
│   ├── src/                    # Main detection logic
│   ├── utils/                  # GPS, Buffer, API clients
│   ├── Dockerfile.edge
│   └── requirements.txt
├── backend/                    # FastAPI server & reporting
│   ├── app/                    # Routes, Models, Services
│   ├── Dockerfile.backend
│   └── requirements.txt
├── frontend/                   # React Vite Dashboard
│   ├── src/                    # App, Components
│   └── Dockerfile.frontend
├── ai_pipeline/                # Training & Export Scripts
│   ├── data/
│   └── scripts/
├── database/                   # PostgreSQL Initialization
└── docker-compose.yml          # Local Stack Orchestration
```

## 🚀 Quick Start (Local Docker)

The easiest way to test the full stack locally is via `docker-compose`.

1. **Set Environment Variables**:
   In your shell, export your SendGrid API key if you want email alerts:
   ```bash
   export SENDGRID_API_KEY="your-api-key"
   ```

2. **Start the Stack**:
   From the root `smart_helmet` directory, run:
   ```bash
   docker-compose up --build
   ```
   This will spin up:
   * PostgreSQL database (Port `5432`)
   * FastAPI Backend (Port `8000`)
   * React Dashboard (Port `5173`)

3. **Access the Dashboard**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

4. **Run the Edge AI Node**:
   To simulate the helmet on your local machine (using your webcam):
   ```bash
   cd edge_ai
   pip install -r requirements.txt
   python src/main.py
   ```
   *Note: To run headless or use an RTSP stream, modify the `cv2.VideoCapture` inside `src/main.py`.*

## 🧠 AI Training & Edge Deployment

Navigate to the `ai_pipeline/scripts` directory to find utilities for retraining the YOLO model on custom datasets and exporting the model to ONNX or TensorRT formats for hardware acceleration on Jetson Orin Nano.

```bash
cd ai_pipeline/scripts
python train.py
python export_tensorrt.py
```

## 🔐 Privacy & Security

* Video is stored temporarily in RAM; permanent storage only occurs upon a flagged violation.
* All APIs are structured for JWT authentication (placeholder included in backend).
* Dashboard UI strictly isolates evidence access.

## 🛠️ Hardware Requirements (Production)
* **Compute Node**: Jetson Orin Nano / Raspberry Pi 5.
* **Camera**: 90° FOV 1080p USB/MIPI Camera mounted on the chin.
* **Network**: 4G/LTE Modem for real-time reporting.
