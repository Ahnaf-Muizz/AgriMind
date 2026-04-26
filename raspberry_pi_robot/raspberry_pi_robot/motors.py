import time

import RPi.GPIO as GPIO

import config


class MotorController:
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.use_pwm = bool(getattr(config, "MOTOR_PWM_ENABLED", True))
        self.use_enable_pins = bool(getattr(config, "MOTOR_USE_ENABLE_PINS", True))

        GPIO.setup(config.MOTOR_IN1_PIN, GPIO.OUT)
        GPIO.setup(config.MOTOR_IN2_PIN, GPIO.OUT)
        GPIO.setup(config.MOTOR_IN3_PIN, GPIO.OUT)
        GPIO.setup(config.MOTOR_IN4_PIN, GPIO.OUT)
        self.pwm_left = None
        self.pwm_right = None

        if self.use_enable_pins:
            GPIO.setup(config.MOTOR_ENA_PIN, GPIO.OUT)
            GPIO.setup(config.MOTOR_ENB_PIN, GPIO.OUT)

        if self.use_pwm and self.use_enable_pins:
            self.pwm_left = GPIO.PWM(config.MOTOR_ENA_PIN, config.PWM_FREQUENCY)
            self.pwm_right = GPIO.PWM(config.MOTOR_ENB_PIN, config.PWM_FREQUENCY)
            self.pwm_left.start(0)
            self.pwm_right.start(0)
        elif self.use_enable_pins:
            GPIO.output(config.MOTOR_ENA_PIN, GPIO.LOW)
            GPIO.output(config.MOTOR_ENB_PIN, GPIO.LOW)

    @staticmethod
    def _clamp_speed(speed: float) -> float:
        return max(0.0, min(100.0, speed))

    def set_speed(self, left_speed: float, right_speed: float) -> None:
        left = self._clamp_speed(left_speed + config.LEFT_MOTOR_TRIM)
        right = self._clamp_speed(right_speed + config.RIGHT_MOTOR_TRIM)
        if not self.use_enable_pins:
            return
        if not self.use_pwm:
            GPIO.output(config.MOTOR_ENA_PIN, GPIO.HIGH if left > 0 else GPIO.LOW)
            GPIO.output(config.MOTOR_ENB_PIN, GPIO.HIGH if right > 0 else GPIO.LOW)
            return
        self.pwm_left.ChangeDutyCycle(left)
        self.pwm_right.ChangeDutyCycle(right)

    def forward(self, speed_left=None, speed_right=None) -> None:
        speed_left = speed_left if speed_left is not None else config.LEFT_MOTOR_BASE_SPEED
        speed_right = speed_right if speed_right is not None else config.RIGHT_MOTOR_BASE_SPEED
        GPIO.output(config.MOTOR_IN1_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN2_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN3_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN4_PIN, GPIO.LOW)
        self.set_speed(speed_left, speed_right)

    def backward(self, speed_left=None, speed_right=None) -> None:
        speed_left = speed_left if speed_left is not None else config.LEFT_MOTOR_BASE_SPEED
        speed_right = speed_right if speed_right is not None else config.RIGHT_MOTOR_BASE_SPEED
        GPIO.output(config.MOTOR_IN1_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN2_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN3_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN4_PIN, GPIO.HIGH)
        self.set_speed(speed_left, speed_right)

    def turn_left(self, speed=45) -> None:
        GPIO.output(config.MOTOR_IN1_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN2_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN3_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN4_PIN, GPIO.LOW)
        self.set_speed(speed, speed)

    def turn_right(self, speed=45) -> None:
        GPIO.output(config.MOTOR_IN1_PIN, GPIO.HIGH)
        GPIO.output(config.MOTOR_IN2_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN3_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN4_PIN, GPIO.HIGH)
        self.set_speed(speed, speed)

    def stop(self) -> None:
        self.set_speed(0, 0)
        GPIO.output(config.MOTOR_IN1_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN2_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN3_PIN, GPIO.LOW)
        GPIO.output(config.MOTOR_IN4_PIN, GPIO.LOW)

    def demo_motion(self) -> None:
        self.forward()
        time.sleep(1.0)
        self.turn_left()
        time.sleep(0.7)
        self.turn_right()
        time.sleep(0.7)
        self.backward()
        time.sleep(1.0)
        self.stop()

    def cleanup(self) -> None:
        self.stop()
        if self.pwm_left is not None:
            self.pwm_left.stop()
        if self.pwm_right is not None:
            self.pwm_right.stop()
        GPIO.cleanup()
