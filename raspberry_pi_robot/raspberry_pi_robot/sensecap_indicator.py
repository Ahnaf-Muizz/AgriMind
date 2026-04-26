import json
from datetime import datetime

import config

try:
    import serial  # type: ignore
except ImportError:
    serial = None


class SenseCAPIndicator:
    def __init__(self) -> None:
        self.enabled = config.SENSECAP_ENABLED
        self.ser = None
        if not self.enabled:
            return
        if serial is None:
            print("pyserial not installed. SenseCAP output disabled.")
            self.enabled = False
            return
        ports = getattr(config, "SENSECAP_SERIAL_PORTS", ())
        # Backward compatibility with older config that used one port string.
        if not ports:
            single_port = getattr(config, "SENSECAP_SERIAL_PORT", None)
            ports = (single_port,) if single_port else ()

        for port in ports:
            candidate_ser = None
            try:
                candidate_ser = serial.Serial(
                    port,
                    config.SENSECAP_BAUDRATE,
                    timeout=1,
                )
                print(f"SenseCAP connected on {port}")
                self.ser = candidate_ser
                break
            except Exception:
                if candidate_ser is not None and candidate_ser.is_open:
                    candidate_ser.close()
                continue

        if self.ser is None:
            print("SenseCAP serial open failed on all configured ports.")
            self.enabled = False

    def send_status(self, payload: dict) -> None:
        if not self.enabled or self.ser is None:
            return
        message = {
            "ts": datetime.now().isoformat(),
            "type": "robot_status",
            "data": payload,
        }
        line = json.dumps(message) + "\n"
        print("SenseCAP TX:", line.strip())
        self.ser.write(line.encode("utf-8"))

    def close(self) -> None:
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
