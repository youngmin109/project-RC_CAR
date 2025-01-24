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
current_speed = 20
max_speed = 45
current_angle = 80
angle_step = 25

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

# 서보 모터 각도 조절 함수 (쓰레딩 적용)
def set_servo_angle(angle):
    def servo_thread():
        duty = 3.0 + (angle / 180.0) * 9.5
        servo_pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        servo_pwm.ChangeDutyCycle(0)
    
    thread = threading.Thread(target=servo_thread)
    thread.start()

# 키보드 이벤트 핸들러
def key_press(event):
    global current_angle
    if event.keysym == 'Left':
        current_angle = max(0, current_angle - angle_step)
        set_servo_angle(current_angle)
    elif event.keysym == 'Right':
        current_angle = min(180, current_angle + angle_step)
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