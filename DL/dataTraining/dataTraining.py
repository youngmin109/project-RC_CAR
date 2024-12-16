import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import subprocess
import shlex
import datetime
import os
import threading

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 전진 방향 제어 핀
IN2 = 27        # DC 모터 후진 방향 제어 핀
ENA = 18        # DC 모터 속도 제어 핀 (PWM)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터 PWM (50Hz)
dc_motor_pwm = GPIO.PWM(ENA, 100)    # DC 모터 PWM (100Hz)

servo_pwm.start(0)
dc_motor_pwm.start(30)  # 초기 속도 30

# === 변수 설정 ===
current_angle = 90  # 서보모터 초기 각도
current_speed = 30  # DC 모터 초기 속도
ANGLE_INCREMENT = 5
SPEED_INCREMENT = 5
MAX_SPEED = 100
MIN_SPEED = 0

# === 이미지 저장 경로 ===
save_path = "/home/HyoChan/RC_CAR/DL/dataTraining/images"
os.makedirs(save_path, exist_ok=True)

# === 서보모터 제어 함수 ===
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 각도 → 듀티사이클 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.05)  # 조향 속도 개선 (부드럽고 빠르게)

# === DC 모터 제어 함수 ===
def motor_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

def motor_backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"후진: 속도 {current_speed}%")

def motor_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# === libcamera를 사용한 이미지 저장 함수 ===
def save_image(state_name):
    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    filename = os.path.join(save_path, f"{now}_{state_name}.jpg")
    cmd = f"libcamera-still -o {filename} --width 1280 --height 720 --nopreview"
    subprocess.run(shlex.split(cmd))
    print(f"이미지 저장: {filename}")

# === 키 입력 이벤트 ===
def on_press(key):
    global current_angle, current_speed
    try:
        if key == keyboard.Key.up:  # 전진 (속도 5 증가)
            current_speed = min(current_speed + SPEED_INCREMENT, MAX_SPEED)
            motor_forward()

        elif key == keyboard.Key.down:  # 후진 (속도 5 감소)
            current_speed = max(current_speed - SPEED_INCREMENT, MIN_SPEED)
            motor_backward()

        elif key == keyboard.Key.space:  # 정지
            motor_stop()
            current_speed = 0

        elif key == keyboard.Key.left:  # 왼쪽 방향 (조향 각도 감소)
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"왼쪽 회전: 각도 {current_angle}도")

        elif key == keyboard.Key.right:  # 오른쪽 방향 (조향 각도 증가)
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"오른쪽 회전: 각도 {current_angle}도")

        elif key.char == 'z':  # 조향 초기화 및 이미지 저장
            print("조향 초기화 중...")
            while current_angle > 90:
                current_angle -= ANGLE_INCREMENT
                set_servo_angle(current_angle)
            while current_angle < 90:
                current_angle += ANGLE_INCREMENT
                set_servo_angle(current_angle)
            set_servo_angle(90)
            print("조향 초기화 완료: 각도 90도")
            save_image("Straight")  # 이미지 저장

    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:  # ESC 키를 누르면 프로그램 종료
        print("프로그램 종료")
        return False

# === 프로그램 실행 ===
try:
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()
except KeyboardInterrupt:
    pass
finally:
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램 종료 및 GPIO 정리 완료")
