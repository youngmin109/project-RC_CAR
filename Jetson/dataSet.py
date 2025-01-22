import Jetson.GPIO as GPIO
import time
import cv2
import os
import threading
import tkinter as tk
from tkinter import messagebox

# GPIO 설정
SERVO_PIN = 32  # 서보 모터 PWM 핀
DC_PWM_PIN = 33  # DC 모터 PWM 핀
IN1_PIN = 31  # DC 모터 IN1
IN2_PIN = 29  # DC 모터 IN2

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(DC_PWM_PIN, GPIO.OUT)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)

# PWM 초기화
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(7.5)
dc_pwm = GPIO.PWM(DC_PWM_PIN, 100)
dc_pwm.start(0)

# 속도 및 각도 초기값
current_speed = 0
max_speed = 45
current_angle = 90
angle_step = 25
sleep_time = 0.5

# 최대 각도 설정
min_angle = 40
max_angle = 140

# 데이터셋 디렉토리 설정
data_dir = "dataSet"
os.makedirs(data_dir, exist_ok=True)
angle_ranges = {
    "40": 40,
    "65": 65,
    "90": 90,
    "115": 115,
    "140": 140
}
for folder in angle_ranges.keys():
    os.makedirs(os.path.join(data_dir, folder), exist_ok=True)

# DC 모터 전진 및 후진 함수
def move_forward():
    GPIO.output(IN1_PIN, GPIO.HIGH)
    GPIO.output(IN2_PIN, GPIO.LOW)
    dc_pwm.ChangeDutyCycle(max_speed)

def move_backward():
    GPIO.output(IN1_PIN, GPIO.LOW)
    GPIO.output(IN2_PIN, GPIO.HIGH)
    dc_pwm.ChangeDutyCycle(max_speed)

def stop_motors():
    dc_pwm.ChangeDutyCycle(0)

# 서보 모터 각도 조절 및 이미지 저장 함수 (쓰레딩 적용)
def set_servo_angle(angle):
    if angle < min_angle or angle > max_angle:
        print("각도 범위를 벗어났습니다.")
        return

    def servo_thread():
        duty = 3.0 + (angle / 180.0) * 9.5
        servo_pwm.ChangeDutyCycle(duty)
        time.sleep(sleep_time)
        servo_pwm.ChangeDutyCycle(0)
        capture_image(angle)
    
    thread = threading.Thread(target=servo_thread)
    thread.start()

# 이미지 캡처 함수
def capture_image(angle):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -16)  # 노출 조정
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)  # 밝기 조정
    cap.set(cv2.CAP_PROP_CONTRAST, 30)  # 대비 조정
    ret, frame = cap.read()
    cap.release()
    if ret:
        for folder, ang in angle_ranges.items():
            if angle == ang:
                filename = os.path.join(data_dir, folder, f"image_{int(time.time())}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Captured: {filename}")
                break

# 키보드 이벤트 핸들러
def key_press(event):
    global current_angle
    if event.keysym == 'Left':
        current_angle = max(min_angle, current_angle - angle_step)
        set_servo_angle(current_angle)
    elif event.keysym == 'Right':
        current_angle = min(max_angle, current_angle + angle_step)
        set_servo_angle(current_angle)
    elif event.keysym == 'Up':
        move_forward()
    elif event.keysym == 'Down':
        move_backward()
    elif event.keysym == 'q':
        on_close()

def key_release(event):
    stop_motors()

# Tkinter 창 설정
root = tk.Tk()
root.title("Motor Control")
root.geometry("300x200")

root.bind('<KeyPress>', key_press)
root.bind('<KeyRelease>', key_release)

# 종료 처리 함수
def on_close():
    print("프로그램 종료 중...")
    servo_pwm.stop()
    dc_pwm.stop()
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()