from datetime import datetime
from pathlib import Path
import time

import cv2

import config


class CameraCapture:
    def __init__(self) -> None:
        self.out_dir = Path(config.CAPTURE_DIR)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.capture = None
        camera_indexes = [config.CAMERA_INDEX, *getattr(config, "CAMERA_INDEX_FALLBACKS", ())]
        tried = []
        open_retries = int(getattr(config, "CAMERA_OPEN_RETRIES", 2))
        backends = (cv2.CAP_V4L2, cv2.CAP_ANY)

        for index in camera_indexes:
            if index in tried:
                continue
            tried.append(index)
            for backend in backends:
                for _ in range(max(1, open_retries)):
                    cap = cv2.VideoCapture(index, backend)
                    if not cap.isOpened():
                        cap.release()
                        continue
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)
                    ok, _ = cap.read()
                    if ok:
                        self.capture = cap
                        print(f"Camera connected on index {index} backend={backend}")
                        break
                    cap.release()
                    time.sleep(0.1)
                if self.capture is not None:
                    break
            if self.capture is not None:
                break

        if self.capture is None:
            tried_text = ", ".join(str(idx) for idx in tried)
            raise RuntimeError(f"Camera not detected on indices [{tried_text}].")

    def snap(self, prefix: str = "crop") -> str:
        # Drop buffered frames so saved image reflects current view/focus.
        warmup_frames = int(getattr(config, "CAMERA_WARMUP_FRAMES", 10))
        for _ in range(max(1, warmup_frames)):
            self.capture.grab()
        read_retries = int(getattr(config, "CAMERA_READ_RETRIES", 3))
        ok, frame = False, None
        for _ in range(max(1, read_retries)):
            ok, frame = self.capture.read()
            if ok:
                break
            time.sleep(0.05)
        if not ok or frame is None:
            raise RuntimeError("Failed to capture frame from camera after retries.")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        out_path = self.out_dir / f"{prefix}_{ts}.jpg"
        cv2.imwrite(str(out_path), frame)
        return str(out_path)

    def close(self) -> None:
        self.capture.release()
