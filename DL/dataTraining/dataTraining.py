import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
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

# 카메라 스트리밍 및 이미지 저장 함수
def camera_streaming():
    save_path = "/home/pi/Image/"
    capture_interval = 2  # 2초마다 캡처
    last_capture_time = time.time()

    # OpenCV 카메라 초기화
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다!")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("카메라 프레임을 읽을 수 없습니다!")
                break

            # 전처리: 높이를 절반으로 잘라 저장
            height, _, _ = frame.shape
            save_image = frame[int(height / 2):, :, :]
            save_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2YUV)
            save_image = cv2.GaussianBlur(save_image, (3, 3), 0)
            save_image = cv2.resize(save_image, (200, 66))

            # 화면에 이미지 표시
            cv2.imshow('frame', frame)

            # 주기적으로 이미지 캡처 및 저장
            current_time = time.time()
            if current_time - last_capture_time >= capture_interval:
                now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                angle = current_angle  # 현재 각도를 기준으로 저장
                if angle == 45:
                    filename = f"{save_path}left_{now}.jpg"
                elif angle == 90:
                    filename = f"{save_path}center_{now}.jpg"
                elif angle == 135:
                    filename = f"{save_path}right_{now}.jpg"
                else:
                    filename = f"{save_path}unknown_{now}.jpg"

                if cv2.imwrite(filename, save_image):
                    print(f"이미지 저장 성공: {filename}")
                else:
                    print(f"이미지 저장 실패: {filename}")

                last_capture_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

# 메인 함수
def main():
    camera_thread = threading.Thread(target=camera_streaming, daemon=True)
    camera_thread.start()
    camera_thread.join()

    # GPIO 정리
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
