import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import subprocess
import shlex
import datetime
import threading

# GPIO 핀 설정
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM 설정
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz
dc_motor_pwm = GPIO.PWM(ENA, 100)   # DC 모터: 100Hz

# PWM 시작
servo_pwm.start(0)
dc_motor_pwm.start(0)

# 초기값 설정
current_angle = 90
current_speed = 0

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 각도를 듀티 사이클로 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  # 서보모터가 움직일 시간을 줌
    servo_pwm.ChangeDutyCycle(0)  # 과열 방지
    print(f"서보모터 각도 설정: {angle}도")

# DC 모터 전진 함수 (속도 증가)
def motor_forward():
    global current_speed
    if current_speed < 100:
        current_speed += 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

# DC 모터 속도 감소 함수
def motor_slow_down():
    global current_speed
    if current_speed > 0:
        current_speed -= 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"속도 감소: 속도 {current_speed}%")

# 모터 정지 함수
def motor_stop():
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# 초기 서보모터 각도 설정
set_servo_angle(current_angle)

# 키 입력 처리 함수
def on_press(key):
    global current_angle
    try:
        if key == keyboard.Key.up:  # 위쪽 방향키: DC 모터 전진
            motor_forward()
        elif key == keyboard.Key.down:  # 아래쪽 방향키: DC 모터 속도 감소
            motor_slow_down()
        elif key == keyboard.Key.left:  # 왼쪽 방향키: 서보모터 왼쪽 회전
            current_angle = max(0, current_angle - 5)
            set_servo_angle(current_angle)
        elif key == keyboard.Key.right:  # 오른쪽 방향키: 서보모터 오른쪽 회전
            current_angle = min(180, current_angle + 5)
            set_servo_angle(current_angle)
        elif key == keyboard.Key.space:  # Space 키: 모터 정지
            motor_stop()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("프로그램 종료")
        return False

# 키보드 리스너 함수
def keyboard_listener():
    print("키보드 입력 대기 중...")
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()

# 카메라 스트리밍 및 이미지 저장 함수
def camera_streaming():
    cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 30 --roi 0.2,0.2,0.6,0.6 -o - --camera 0'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    save_path = "/home/pi/Image/"
    buffer = b""
    capture_interval = 2  # 2초마다 캡처
    last_capture_time = time.time()

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', 640, 360)

    try:
        while True:
            current_time = time.time()
            buffer += process.stdout.read(4096)
            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if frame is not None:
                    # 디지털 줌 아웃
                    resized_frame = cv2.resize(frame, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_LINEAR)
                    cv2.imshow('frame', resized_frame)

                    if current_time - last_capture_time >= capture_interval:
                        now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                        if current_angle == 45:
                            image_name = f"left_{now}.jpg"
                        elif current_angle == 90:
                            image_name = f"center_{now}.jpg"
                        elif current_angle == 135:
                            image_name = f"right_{now}.jpg"
                        else:
                            image_name = f"unknown_{now}.jpg"

                        if cv2.imwrite(save_path + image_name, frame):
                            print(f"이미지 저장 성공: {image_name}")
                        else:
                            print(f"이미지 저장 실패: {image_name}")
                        last_capture_time = current_time

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    finally:
        process.terminate()
        cv2.destroyAllWindows()

# 스레드 실행
keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
camera_thread = threading.Thread(target=camera_streaming, daemon=True)

keyboard_thread.start()
camera_thread.start()

keyboard_thread.join()
camera_thread.join()

# GPIO 정리
servo_pwm.stop()
dc_motor_pwm.stop()
GPIO.cleanup()
