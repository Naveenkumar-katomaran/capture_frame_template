# Low-Latency RTSP Viewer

A lightweight, robust Python framework for streaming and rendering high-efficiency RTSP streams (like H.265/HEVC) without latency build-up, dropped reference frames, or excessive CPU polling.

## Files Structure

This package consists of only two necessary files:

### 1. `capture_frame_template.py`
The core engine. It utilizes a **Producer-Consumer Multithreading Model**:
- **Background Thread (Producer):** Uses OpenCV (`cv2.CAP_FFMPEG`) to continuously grab frames from the RTSP stream as fast as they arrive, intentionally discarding older frames and keeping only the absolute newest frame. This prevents the OpenCV internal buffer from filling up and eliminates video delay/ghosting.
- **Main Thread (Consumer):** Safely grabs the most recent frame and handles UI rendering (`cv2.imshow`) or any downstream pipeline integrations (like YOLO inference) on a controlled frame-skip interval, sleeping appropriately to spare CPU cycles. 

### 2. `config.json`
The central configuration file used to dynamically tweak camera and display outputs without needing to edit the source code.

**Fields breakdown:**
* `camera.rtsp_url`: The direct RTSP feed to the IP camera.
* `camera.frame_skip`: How many frames to skip before rendering one to the screen, allowing tuning to save UI render loops.
* `camera.ffmpeg_options`: Essential flags passed specifically to the FFmpeg backend inside OpenCV to force stable networking (e.g., forcing TCP instead of UDP) and buffer limits.
* `display.window_width` / `window_height`: Dimensions for the output UI stream.
* `display.fullscreen`: Boolean to force the stream viewer into edge-to-edge fullscreen mode.

## Usage

Ensure you have OpenCV and Numpy installed. 
Simply run the Python script:

```bash
python capture_frame_template.py
```
*(Press `q` within the stream window to terminate the application gracefully).*
