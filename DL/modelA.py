import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz PWM
dc_motor_pwm = GPIO.PWM(ENA, 100)   # DC 모터: 100Hz PWM

servo_pwm.start(0)
dc_motor_pwm.start(0)

# 초기값 설정
current_angle = 30
current_speed = 0

# === 모델 로드 ===
model = load_model('/home/pi/autonomous_car_model.h5')
print("모델 로드 완료")

# === 함수 정의 ===
def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)
    print(f"서보모터 각도 설정: {angle}도")

def motor_forward():
    global current_speed
    if current_speed < 100:
        current_speed += 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

def motor_stop():
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# === 카메라 스트리밍 설정 ===
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (64, 64))
    normalized = resized / 255.0
    return normalized.reshape(1, 64, 64, 1)

def main():
    # 카메라 초기화
    cap = cv2.VideoCapture(0)  # 0번 카메라 사용

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

            # 전진
            motor_forward()

            # ESC 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("프로그램 종료")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        servo_pwm.stop()
        dc_motor_pwm.stop()
        GPIO.cleanup()
        print("자원을 정리하고 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
