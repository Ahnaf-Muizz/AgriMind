import json
import time
from datetime import datetime

import config
from camera import CameraCapture
from motors import MotorController
from sensecap_indicator import SenseCAPIndicator
from sensors import SensorSuite


def print_help() -> None:
    print("\nCommands:")
    print("  f  -> move forward")
    print("  b  -> move backward")
    print("  l  -> turn left")
    print("  r  -> turn right")
    print("  s  -> stop")
    print("  c  -> capture image")
    print("  d  -> demo motion")
    print("  q  -> quit")


def main() -> None:
    motors = MotorController()
    sensors = SensorSuite()
    camera = None
    try:
        camera = CameraCapture()
    except RuntimeError as exc:
        print(f"Camera disabled: {exc}")
    indicator = SenseCAPIndicator()

    loop_count = 0
    print("Robot controller started.")
    print_help()

    try:
        while True:
            loop_count += 1
            sensor_data = sensors.read_all()
            sensor_data["timestamp"] = datetime.now().isoformat()
            print("Sensors:", json.dumps(sensor_data))
            indicator.send_status(sensor_data)

            if camera is not None and loop_count % config.AUTO_CAPTURE_EVERY_N_LOOPS == 0:
                img_path = camera.snap(prefix="auto")
                print(f"Auto capture saved: {img_path}")

            cmd = input("Enter command (f/b/l/r/s/c/d/q or Enter to continue): ").strip().lower()
            if cmd == "f":
                motors.forward()
            elif cmd == "b":
                motors.backward()
            elif cmd == "l":
                motors.turn_left()
            elif cmd == "r":
                motors.turn_right()
            elif cmd == "s":
                motors.stop()
            elif cmd == "c":
                if camera is None:
                    print("Capture skipped: camera not available.")
                else:
                    img_path = camera.snap(prefix="manual")
                    print(f"Manual capture saved: {img_path}")
            elif cmd == "d":
                motors.demo_motion()
            elif cmd == "q":
                break

            time.sleep(config.LOOP_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopping robot...")
    finally:
        motors.cleanup()
        if camera is not None:
            camera.close()
        indicator.close()
        print("Clean shutdown done.")


if __name__ == "__main__":
    main()
