import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import subprocess
import shlex
import datetime
import threading
# threading 모듈을 통해 키보드 입력 처리와 카메라 스트리밍을 별도로 실행

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

    global current_speed
    
    # 서보모터 각도 수정 전 DC 모터 속도를 줄임
    reduced_speed = max(0, current_speed - 20)  # 속도를 20% 감소
    dc_motor_pwm.ChangeDutyCycle(reduced_speed)
    print(f"서보모터 각도 수정 중, DC 모터 속도 감소: {reduced_speed}%")


    duty = 2 + (angle / 18) # 각도를 듀티 사이클로 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1) # 모터가 움직일 시간을 줌
    servo_pwm.ChangeDutyCycle(0) # 과열 방지를 위해 0의 설정

    # 서보모터 각도 수정 후 DC 모터 속도 복구
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"서보모터 각도 수정 완료, DC 모터 속도 복구: {current_speed}%")


# DC 모터 전진 함수 (속도 증가)
def motor_forward():
    global current_speed
    if current_speed < 100:
        current_speed += 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

# DC 모터 후진 함수 (속도 증가)
def motor_backward():
    global current_speed
    if current_speed < 100:
        current_speed += 5
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"후진: 속도 {current_speed}%")

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
        elif key == keyboard.Key.down:  # 아래쪽 방향키: 속도 감소 또는 후진
            if current_speed > 0:  # 속도가 있는 경우 속도를 줄임
                motor_slow_down()
            else:  # 속도가 0인 경우 후진
                motor_backward()
        elif key == keyboard.Key.left:  # 왼쪽 방향키: 서보모터 왼쪽 회전
            current_angle = max(0, current_angle - 5)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:  # 오른쪽 방향키: 서보모터 오른쪽 회전
            current_angle = min(180, current_angle + 5)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:  # Space 키: 모터 정지
            motor_stop()
    except AttributeError:
        pass


def on_release(key):
    if key == keyboard.Key.esc:
        # esc키 입력시 키보드 스레드 종료
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
    cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 30 -o - --camera 0'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    save_path = "/home/Image"
    buffer = b""
    capture_interval = 1
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
                    cv2.imshow('frame', frame)

                    if current_time - last_capture_time >= capture_interval:
                        now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                        try:
                            if cv2.imwrite(save_path + now + ".jpg", frame):
                                print(f"이미지 저장 성공: {now}")
                            else:
                                print(f"이미지 저장 실패: {now}")
                        except Exception as e:
                            print("이미지 저장 중 에러 발생:", e)
                        last_capture_time = current_time

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        # q입력시 카메라 종료
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