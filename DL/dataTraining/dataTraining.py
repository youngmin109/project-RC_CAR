import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import datetime
import os

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 전진 방향 제어 핀
IN2 = 27        # DC 모터 후진 방향 제어 핀
ENA = 18        # DC 모터 속도 제어 핀 (PWM)

GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터 PWM: 50Hz
dc_motor_pwm = GPIO.PWM(ENA, 100)    # DC 모터 PWM: 100Hz

servo_pwm.start(0)
dc_motor_pwm.start(30)  # 초기 속도 30으로 설정

current_angle = 90  # 서보모터 초기 각도
current_speed = 30  # DC 모터 초기 속도

ANGLE_INCREMENT = 5  # 서보모터 각도 변화량
SPEED_INCREMENT = 5  # 속도 증가 단위
MAX_SPEED = 100      # DC 모터 최대 속도

# === 이미지 저장 경로 설정 ===
save_path = "/home/HyoChan/RC_CAR/DL/dataTraining/images"
os.makedirs(save_path, exist_ok=True)  # 경로가 없으면 생성

# === 서보모터 제어 함수 ===
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 각도 → 듀티사이클 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)

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

# === 이미지 저장 함수 ===
def save_image(state_name):
    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    filename = os.path.join(save_path, f"{now}_{state_name}.jpg")
    img = np.zeros((720, 1280, 3), dtype=np.uint8)  # 예시 이미지 생성 (카메라 연동 필요)
    cv2.imwrite(filename, img)
    print(f"이미지 저장: {filename}")

# === 키 입력 함수 ===
def on_press(key):
    global current_angle, current_speed, last_capture_time
    try:
        if key == keyboard.Key.up:  # 전진
            motor_forward()
        elif key == keyboard.Key.down:  # 정지
            motor_stop()
        elif key == keyboard.Key.left:  # 왼쪽 방향
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:  # 오른쪽 방향
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key.char == 'z':  # 초기화 및 이미지 저장
            while current_angle > 90:  # 각도 복귀 (오른쪽 → 중앙)
                current_angle -= ANGLE_INCREMENT
                set_servo_angle(current_angle)
                time.sleep(0.05)
            while current_angle < 90:  # 각도 복귀 (왼쪽 → 중앙)
                current_angle += ANGLE_INCREMENT
                set_servo_angle(current_angle)
                time.sleep(0.05)
            print("조향 초기화: 각도 90도")
            save_image("Straight")  # 이미지 저장
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:  # ESC 키를 누르면 종료
        print("프로그램 종료")
        return False

# === 주기적으로 이미지 저장 ===
last_capture_time = time.time()
def periodic_capture():
    global last_capture_time
    while True:
        current_time = time.time()
        if current_time - last_capture_time >= 2:  # 2초 간격
            save_image("Periodic")
            last_capture_time = current_time
        time.sleep(0.1)  # CPU 부하 최소화

# === 프로그램 실행 ===
try:
    # 이미지 캡처를 위한 스레드 실행
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
