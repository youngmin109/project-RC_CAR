import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
DC_MOTOR_PIN = 18  # DC 모터 핀 번호

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(DC_MOTOR_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz PWM
dc_motor_pwm = GPIO.PWM(DC_MOTOR_PIN, 100)  # DC 모터: 100Hz PWM

servo_pwm.start(0)
dc_motor_pwm.start(0)

# 초기값 설정
current_speed = 0
current_angle = 30
def main():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)  # 카메라 0번 사용

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            # 이미지 전처리
            processed_frame = preprocess_image(frame)

            # 모델 예측
            prediction = model.predict(processed_frame)
            direction = np.argmax(prediction)  # 0: Left, 1: Right

            # RC카 제어
            if direction == 0:  # Left
                current_angle = 15
                set_servo_angle(current_angle)
                print("왼쪽으로 조향")
            elif direction == 1:  # Right
                current_angle = 45
                set_servo_angle(current_angle)
                print("오른쪽으로 조향")
            else:
                current_angle = 30
                set_servo_angle(current_angle)
                print("정면")

            # 전진
            motor_forward(50)

            # ESC 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("프로그램 종료 중...")

    finally:
        # 자원 정리
        cap.release()
   

if __name__ == "__main__":
    main() # 메인 함수가 호출되지 않았다면 실행되지 않습니다.

# === 모델 로드 ===
try:
    model = load_model('/path/to/your_model.h5')
    print("모델 로드 완료")
    main()  # 메인 함수 실행
except Exception as e:
    print(f"오류 발생: {e}")

# === 함수 정의 ===
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

# === 카메라 이미지 전처리 ===
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (64, 64))
    normalized = resized / 255.0
    return normalized.reshape(1, 64, 64, 1)

def main():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)  # 카메라 0번 사용

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            # 이미지 전처리
            processed_frame = preprocess_image(frame)

            # 모델 예측
            prediction = model.predict(processed_frame)
            direction = np.argmax(prediction)  # 0: Left, 1: Right

            # RC카 제어
            if direction == 0:  # Left
                current_angle = 15
                set_servo_angle(current_angle)
                print("왼쪽으로 조향")
            elif direction == 1:  # Right
                current_angle = 45
                set_servo_angle(current_angle)
                print("오른쪽으로 조향")
            else:
                current_angle = 30
                set_servo_angle(current_angle)
                print("정면")

            # 전진
            motor_forward(50)

            # ESC 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("프로그램 종료 중...")

    finally:
        # 자원 정리
        cap.release()
   
