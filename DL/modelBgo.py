import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import time
import RPi.GPIO as GPIO  # GPIO 제어를 위한 라이브러리
import subprocess

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM 초기화
motor_pwm = GPIO.PWM(ENA, 100)  # 주파수 100Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터 주파수 50Hz
motor_pwm.start(0)
servo_pwm.start(7.5)  # 초기 위치 90도

# 모델 로드
model = load_model("direction_classifier.h5")

# Libcamera를 사용한 실시간 영상 처리
def capture_frame():
    """Libcamera를 사용해 실시간 프레임 캡처."""
    output_path = "live_frame.jpg"
    subprocess.run(["libcamera-still", "-o", output_path, "--immediate", "--nopreview"], check=True)
    return output_path

def process_frame(frame_path):
    """캡처된 프레임을 처리하여 모델 예측."""
    img_size = (64, 64)
    img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        img = cv2.resize(img, img_size)
        img = img / 255.0
        img = np.expand_dims(img, axis=(0, -1))  # 배치 차원 및 채널 추가
        predicted_label = np.argmax(model.predict(img))
        return predicted_label
    else:
        print("Error: Could not read the captured frame.")
        return None

def initialize_servo():
    # 초기 서보모터 값을 30도로 설정
    print("Initializing servo motor to 30 degrees")
    servo_pwm.ChangeDutyCycle(7.5)  # 30도에 해당하는 duty cycle
    time.sleep(0.5)

def control_rc_car(predicted_label):
    if predicted_label == 0:  # Left
        angle = 10
        duty_cycle = 5.0  # 대략적인 값 (왼쪽)
    elif predicted_label == 1:  # Right
        angle = 50
        duty_cycle = 10.0  # 대략적인 값 (오른쪽)
    elif predicted_label == 2:  # Straight
        angle = 30
        duty_cycle = 7.5  # 직진 값
    else:
        angle = 30
        duty_cycle = 7.5  # 기본 직진 값

    speed = 25  # 기본 직진 속도

    # 서보모터 제어
    servo_pwm.ChangeDutyCycle(duty_cycle)
    print(f"Servo Angle: {angle}, Speed: {speed}")

    # DC 모터 제어
    GPIO.output(IN1, GPIO.HIGH if speed > 0 else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if speed > 0 else GPIO.HIGH)
    motor_pwm.ChangeDutyCycle(abs(speed))

# 초기화
initialize_servo()

# 실시간 루프
try:
    while True:
        frame_path = capture_frame()
        predicted_label = process_frame(frame_path)
        if predicted_label is not None:
            control_rc_car(predicted_label)
        time.sleep(0.1)  # 루프 간 간격
except KeyboardInterrupt:
    print("실시간 처리 종료.")
finally:
    motor_pwm.stop()
    servo_pwm.stop()
    GPIO.cleanup()