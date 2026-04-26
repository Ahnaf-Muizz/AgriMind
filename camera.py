from datetime import datetime
from pathlib import Path

import cv2

import config


class CameraCapture:
    def __init__(self) -> None:
        self.capture = cv2.VideoCapture(config.CAMERA_INDEX)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)

        self.out_dir = Path(config.CAPTURE_DIR)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        if not self.capture.isOpened():
            raise RuntimeError("Camera not detected. Check Logitech USB connection.")

    def snap(self, prefix: str = "crop") -> str:
        # Drop a few buffered frames so the saved image reflects current view.
        for _ in range(4):
            self.capture.grab()
        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError("Failed to capture frame from camera.")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        out_path = self.out_dir / f"{prefix}_{ts}.jpg"
        cv2.imwrite(str(out_path), frame)
        return str(out_path)

    def close(self) -> None:
        self.capture.release()
