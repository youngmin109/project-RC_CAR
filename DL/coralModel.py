import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import RPi.GPIO as GPIO
import time
import subprocess
import shlex

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
DC_MOTOR_PIN = 18  # DC 모터 핀 번호

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(DC_MOTOR_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz PWM
dc_motor_pwm = GPIO.PWM(DC_MOTOR_PIN, 100)  # DC 모터: 100Hz PWM

servo_pwm.start(0)
dc_motor_pwm.start(20)  # DC 모터 직진 속도 설정

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
    cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 15 -o -'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    buffer = b""
    try:
        while True:
            buffer += process.stdout.read(4096)
            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    print("프레임을 읽을 수 없습니다.")
                    continue

                # 이미지 전처리
                processed_frame = preprocess_image(frame)

                # 모델 예측
                prediction = model.predict(processed_frame)
                direction = np.argmax(prediction)  # 0: Left, 1: Right

                # RC카 제어
                if direction == 0:
                    set_servo_angle(15)  # 왼쪽
                    print("왼쪽으로 조향")
                elif direction == 1:
                    set_servo_angle(45)  # 오른쪽
                    print("오른쪽으로 조향")
                else:
                    set_servo_angle(30)  # 정면
                    print("정면")

                # 전진
                motor_forward(20)

    except KeyboardInterrupt:
        print("프로그램 종료 중...")

    finally:
        process.terminate()
        servo_pwm.stop()
        dc_motor_pwm.stop()
        GPIO.cleanup()
        print("자원을 정리하고 프로그램을 종료합니다.")

# === 메인 실행 ===
if __name__ == "__main__":
    model_path = '/home/HyoChan/RC_CAR/autonomous_car_model.h5'  # H5 모델 경로
    model = load_model(model_path)
    print("모델 로드 완료")
    drive_model(model)