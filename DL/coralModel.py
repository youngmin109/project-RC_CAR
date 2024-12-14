from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import RPi.GPIO as GPIO
import time

# === GPIO 설정 ===
SERVO_PIN = 12
DC_MOTOR_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(DC_MOTOR_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)
dc_motor_pwm = GPIO.PWM(DC_MOTOR_PIN, 100)

servo_pwm.start(0)
dc_motor_pwm.start(0)

# === 데이터 전처리 ===
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (64, 64))
    normalized = resized / 255.0
    return normalized.reshape(1, 64, 64, 1)

# === RC카 제어 ===
def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)
    print(f"서보모터 각도 설정: {angle}도")

def motor_forward(speed):
    dc_motor_pwm.ChangeDutyCycle(speed)
    print(f"전진: 속도 {speed}%")

def motor_stop():
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# === 실시간 주행 ===
def drive_model(model):
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    raw_capture = PiRGBArray(camera, size=(640, 480))

    print("카메라 초기화 완료")
    time.sleep(2)

    try:
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            image = frame.array

            # 이미지 전처리
            processed_frame = preprocess_image(image)

            # 모델 예측
            prediction = model.predict(processed_frame)
            direction = np.argmax(prediction)  # 0: Left, 1: Right

            # RC카 제어
            if direction == 0:
                set_servo_angle(15)
                print("왼쪽으로 조향")
            elif direction == 1:
                set_servo_angle(45)
                print("오른쪽으로 조향")
            else:
                set_servo_angle(30)
                print("정면")

            # 전진
            motor_forward(50)

            raw_capture.truncate(0)

    except KeyboardInterrupt:
        print("프로그램 종료 중...")

    finally:
        camera.close()
        servo_pwm.stop()
        dc_motor_pwm.stop()
        GPIO.cleanup()
        print("자원을 정리하고 프로그램을 종료합니다.")

# === 메인 실행 ===
if __name__ == "__main__":
    model = load_model('/home/pi/autonomous_car_model.h5')
    print("모델 로드 완료")
    drive_model(model)
