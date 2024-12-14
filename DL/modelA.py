import os
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate
import RPi.GPIO as GPIO
import time

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

# === Edge TPU 모델 로드 ===
def load_tpu_model(model_path):
    """
    Edge TPU 모델 로드 함수
    """
    return Interpreter(
        model_path=model_path,
        experimental_delegates=[load_delegate('libedgetpu.so.1')]
    )

# === RC카 제어 ===
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

# === 이미지 전처리 ===
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (64, 64))
    normalized = resized / 255.0
    return normalized.reshape(1, 64, 64, 1)

# === 실시간 주행 ===
def drive_model(interpreter):
    cap = cv2.VideoCapture(0)  # 카메라 0번 사용

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    # 입력과 출력 텐서 정보 가져오기
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            # 이미지 전처리
            processed_frame = preprocess_image(frame)

            # 모델 예측
            interpreter.set_tensor(input_details[0]['index'], processed_frame)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            direction = np.argmax(output_data)  # 0: Left, 1: Right

            # RC카 제어
            if direction == 0:
                set_servo_angle(15)  # 왼쪽
                print("왼쪽으로 조향")
            elif direction == 1:
                set_servo_angle(45)  # 오른쪽
                print("오른쪽으로 조향")
            else:
                set_servo_angle(30)  # 정면
                print("정면")

            # 전진
            motor_forward(50)

            # ESC 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        print("프로그램 종료 중...")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        servo_pwm.stop()
        dc_motor_pwm.stop()
        GPIO.cleanup()
        print("자원을 정리하고 프로그램을 종료합니다.")

# === 메인 실행 ===
if __name__ == "__main__":
    model_path = '/home/pi/autonomous_car_model.tflite'  # TFLite 모델 경로
    interpreter = load_tpu_model(model_path)
    interpreter.allocate_tensors()  # Edge TPU 인터프리터 준비
    print("Edge TPU 모델 로드 완료")

    drive_model(interpreter)
