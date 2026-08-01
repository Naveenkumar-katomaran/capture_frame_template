Here's a simple and professional `README.md` for your project.

# RTSP Frame Capture Template

A simple and reusable Python template for capturing frames from an RTSP stream with **low latency**, **automatic reconnection**, and **threaded frame grabbing** using OpenCV.

## Features

* Low-latency RTSP streaming
* Background thread for continuous frame capture
* Always returns the latest frame
* Automatic reconnection on stream failure
* Thread-safe frame access
* Configurable frame skipping
* Logging for debugging and monitoring

## Requirements

* Python 3.10+
* OpenCV (`opencv-python`)
* NumPy

Install the required packages:

```bash
pip install opencv-python numpy
```

```bash
sudo add-apt-repository ppa:savoury1/ffmpeg4
sudo apt update
sudo apt install ffmpeg
```

## Project Structure

```text
.
├── main.py
└── README.md
```

## Configuration

Open `main.py` and update the following values if needed:

### RTSP URL

```python
DEFAULT_RTSP_URL = "rtsp://<camera-ip>/stream"
```

You can also set the RTSP URL using an environment variable:

```bash
export RTSP_URL="rtsp://<camera-ip>/stream"
```

### Frame Skip

```python
Frame_skip = 10
```

Displays every 10th frame. Increase this value to reduce CPU usage.

## Run

```bash
python main.py
```

Press **Q** to exit the application.

## How It Works

1. Opens the RTSP stream using OpenCV and FFmpeg.
2. Starts a background thread to continuously capture frames.
3. Stores only the latest frame in memory.
4. The main loop reads and processes the newest frame.
5. Automatically reconnects if the RTSP stream is disconnected.

## Use Cases

* Object Detection (YOLO)
* Face Recognition
* License Plate Recognition (LPR)
* People Counting
* Video Analytics
* Any OpenCV-based computer vision application

## Notes

* Optimized for low-latency RTSP streaming.
* Designed to minimize frame buffering.
* Suitable for H.264 and H.265 (HEVC) RTSP streams.
* Can be used as a base template for AI and computer vision projects.

## License

This project is provided as a reusable template. Modify and use it according to your project requirements.

You can also add sections like **Troubleshooting**, **Known Issues**, or **Future Improvements** later as the project grows.
