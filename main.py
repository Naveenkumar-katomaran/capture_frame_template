#!/usr/bin/env python3
"""
Professional low-latency RTSP viewer with threaded frame grabber.
Fixes HEVC 'Could not find ref with POC' ghosting/blurring.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Optional

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
import json

def load_config(path="config.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Failed to load {path}: {e}")
        return {}

CONFIG = load_config()

camera_config = CONFIG.get("camera", {})
display_config = CONFIG.get("display", {})

RTSP_URL = camera_config.get("rtsp_url", 0)

Frame_skip = camera_config.get("frame_skip", 10)

# ---------------- Display ---------------

WINDOW_NAME = display_config.get("window_name", "RTSP Stream")

# Softer options – still low latency but much more stable with HEVC
FFMPEG_OPTIONS = camera_config.get(
    "ffmpeg_options",
    "rtsp_transport;tcp|"
    "fflags;nobuffer|"
    "flags;low_delay|"
    "max_delay;500000|"
    "analyzeduration;1000000|"
    "probesize;1000000"
)


class ThreadedCamera:
    """
    Continuously grabs frames in a background thread.
    Always returns the newest frame (old frames are discarded).
    This prevents the HEVC reference-frame errors and ghosting.
    """

    def __init__(self, source: str | int):
        self.source = source
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.ret = False
        self.running = False
        self.lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        self.cap = self._open_capture(self.source)
        if self.cap is None:
            return False

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True

    def _open_capture(self, source: str | int) -> Optional[cv2.VideoCapture]:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = FFMPEG_OPTIONS


        log.info("Opening stream: %s", source)
        cap = cv2.VideoCapture(str(source), cv2.CAP_FFMPEG)

        # Retry a few times
        for attempt in range(1, 4):
            if cap.isOpened():
                break
            log.warning("Open attempt %d failed – retrying...", attempt)
            cap.release()
            time.sleep(1.5)
            cap = cv2.VideoCapture(str(source), cv2.CAP_FFMPEG)

        if not cap.isOpened():
            log.error("Failed to open source")
            return None

        # Keep buffer small and try to use hardware acceleration
        # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)

        try:
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)
        except Exception:
            pass

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        log.info("Stream opened: %dx%d @ %.1f FPS", w, h, fps if fps > 0 else 0)
        return cap

    def _update(self) -> None:
        """Background thread – always keeps the latest frame."""
        while self.running:
            if self.cap is None:
                break

            ret, frame = self.cap.read()
            if not ret:
                log.warning("Frame grab failed – attempting reconnect...")
                self.cap.release()
                time.sleep(2)
                self.cap = self._open_capture(self.source)
                if self.cap is None:
                    self.running = False
                    break
                continue

            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self) -> tuple[bool, Optional[np.ndarray]]:
        with self.lock:
            # Return frame and clear it so we don't process/imshow it twice
            frame = self.frame
            self.frame = None
            return self.ret, frame

    def stop(self) -> None:
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2.0)
        if self.cap is not None:
            self.cap.release()
        log.info("Camera stopped")


def main() -> None:
    source = os.getenv("RTSP_URL", RTSP_URL)

    cam = ThreadedCamera(source)
    if not cam.start():
        log.error("Could not start camera")
        return

    log.info("Press 'q' to quit")

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        WINDOW_NAME,
        CONFIG["display"]["window_width"],
        CONFIG["display"]["window_height"]
    )

    if CONFIG["display"]["fullscreen"]:

        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

    try:
        frame_count = 0
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                # Crucial: Sleep briefly in the main loop so we don't burn 100% CPU
                time.sleep(0.005)
                continue

            frame_count += 1
            if frame_count % Frame_skip == 0:
                cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        log.info("Interrupted by user")

    finally:
        cam.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
