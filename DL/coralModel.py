import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, Flatten, Dense
from tensorflow.keras.optimizers import Adam
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

# === 데이터 로드 ===
def load_data(data_dir):
    image_paths = []
    labels = []

    for file_name in os.listdir(data_dir):
        if file_name.lower().startswith('left'):
            image_paths.append(os.path.join(data_dir, file_name))
            labels.append(0)  # Left: 0
        elif file_name.lower().startswith('right'):
            image_paths.append(os.path.join(data_dir, file_name))
            labels.append(1)  # Right: 1

    images = []
    for image_path in image_paths:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            resized = cv2.resize(image, (64, 64))
            images.append(resized / 255.0)  # Normalize

    return np.array(images).reshape(-1, 64, 64, 1), np.array(labels)

# === 모델 생성 및 학습 ===
def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 1)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(2, activation='softmax')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(model, X_train, y_train, epochs=10):
    model.fit(X_train, y_train, validation_split=0.2, epochs=epochs, batch_size=32)
    model.save('/home/pi/autonomous_car_model.h5')
    print("모델 학습 및 저장 완료")

# === 데이터 학습 ===
data_dir = '/home/pi/images'  # 데이터 경로 설정
X_train, y_train = load_data(data_dir)
model = create_model()
train_model(model, X_train, y_train, epochs=10)

# === 데이터 전처리 ===
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (64, 64))
    normalized = resized / 255.0
    return normalized.reshape(1, 64, 64, 1)

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

# === 실시간 주행 ===
def drive_model(model):
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
    model = load_model('/home/pi/autonomous_car_model.h5')
    print("모델 로드 완료")
    drive_model(model)
