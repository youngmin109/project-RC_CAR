import RPi.GPIO as GPIO
import time
from pynput import keyboard
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
ANGLE_INCREMENT = 3  # 더 미세한 각도 조정
SPEED_INCREMENT = 2  # 더 느린 속도 증가
MAX_SPEED = 50  # 최대 속도를 낮춤
MIN_SPEED = 10  # 최소 속도 설정

# 조향 각도 범위에 따른 폴더 설정 (직진 범위를 더 줄임)
angle_folders = {
    "left": range(0, 85),  # 0~84도는 left 폴더
    "straight": range(85, 96),  # 85~95도는 straight 폴더
    "right": range(96, 181)  # 96~180도는 right 폴더
}
base_save_path = "/home/HyoChan/RC_CAR/DL/dataTraining/images"
for folder in angle_folders:
    os.makedirs(os.path.join(base_save_path, folder), exist_ok=True)

# === 서보모터 제어 함수 ===
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 각도 → 듀티사이클 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.02)  # 조향 떨림 방지

# === DC 모터 제어 함수 ===
def motor_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

def motor_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# === libcamera를 사용한 이미지 저장 함수 ===
def save_image():
    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    # 조향 각도에 따라 저장 폴더 결정
    for folder, angle_range in angle_folders.items():
        if current_angle in angle_range:
            save_path = os.path.join(base_save_path, folder)
            filename = os.path.join(save_path, f"{now}.jpg")
            cmd = f"libcamera-still -o {filename} --width 1280 --height 720 --nopreview"
            subprocess.run(shlex.split(cmd))
            print(f"이미지 저장: {filename}")
            break

# === 주기적으로 이미지 저장 ===
def periodic_capture():
    while True:
        save_image()
        time.sleep(2)  # 2초마다 이미지 저장

# === 키 입력 이벤트 ===
def on_press(key):
    global current_angle, current_speed
    try:
        if key == keyboard.Key.up:  # 전진 (속도 2 증가)
            current_speed = min(current_speed + SPEED_INCREMENT, MAX_SPEED)
            motor_forward()

        elif key == keyboard.Key.down:  # 전진 속도 감소
            current_speed = max(current_speed - SPEED_INCREMENT, MIN_SPEED)
            if current_speed > 0:
                motor_forward()
            else:
                motor_stop()

        elif key == keyboard.Key.space:  # 정지
            motor_stop()
            current_speed = MIN_SPEED  # 정지 후 기본 속도로 초기화

        elif key == keyboard.Key.left:  # 왼쪽 방향 (조향 각도 감소)
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"왼쪽 회전: 각도 {current_angle}도")

        elif key == keyboard.Key.right:  # 오른쪽 방향 (조향 각도 증가)
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"오른쪽 회전: 각도 {current_angle}도")

        elif key.char == 'z':  # 조향 초기화
            print("조향 초기화 중...")
            current_angle = 90
            set_servo_angle(90)
            print("조향 초기화 완료: 각도 90도")

    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:  # ESC 키를 누르면 프로그램 종료
        print("프로그램 종료")
        return False

# === 프로그램 실행 ===
try:
    # 이미지 캡처 스레드 실행
    capture_thread = threading.Thread(target=periodic_capture, daemon=True)
    capture_thread.start()

    # 키보드 입력 감지
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
