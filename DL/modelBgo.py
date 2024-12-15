import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import time
import subprocess

# 모델 로드
try:
    model = load_model("direction_classifier.h5")
    print("모델이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"모델 로드 중 오류 발생: {e}")
    exit()

# Libcamera를 사용한 실시간 영상 처리
def capture_frame():
    """Libcamera를 사용해 실시간 프레임 캡처."""
    output_path = "live_frame.jpg"
    try:
        subprocess.run(
            ["libcamera-still", "-o", output_path, "--immediate", "--nopreview"], check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Libcamera 실행 중 오류 발생: {e}")
        return None

def process_frame(frame_path):
    """캡처된 프레임을 처리하여 모델 예측."""
    img_size = (64, 64)
    try:
        img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            img = cv2.resize(img, img_size)
            img = img / 255.0
            img = np.expand_dims(img, axis=(0, -1))  # 배치 차원 및 채널 추가
            predicted_label = np.argmax(model.predict(img))
            return predicted_label
        else:
            print("Error: Could not read the captured frame.")
            return None
    except Exception as e:
        print(f"프레임 처리 중 오류 발생: {e}")
        return None

def initialize_servo():
    # 초기 서보모터 값을 30도로 설정
    initial_angle = 30
    print(f"Initializing servo motor to {initial_angle} degrees")
    # 실제 서보모터 초기화 로직 (GPIO 제어 또는 시리얼 통신 등)
    # send_to_servo(initial_angle)

initialize_servo()

def control_rc_car(predicted_label):
    try:
        if predicted_label == 0:  # Left
            angle = 10
        elif predicted_label == 1:  # Right
            angle = 50
        elif predicted_label == 2:  # Straight
            angle = 30
        else:
            angle = 30  # Default to straight

        speed = 25  # 기본 직진 속도

        # RC카의 제어 명령 출력 (실제로는 RC카에 명령 전달)
        print(f"Angle: {angle}, Speed: {speed}")
        
        # 예: 실제 RC카 제어 로직 (시리얼 통신 또는 GPIO 제어)
        # send_to_rc_car(angle, speed)
    except Exception as e:
        print(f"RC카 제어 중 오류 발생: {e}")

# 실시간 루프
try:
    while True:
        frame_path = capture_frame()
        if frame_path is None:
            print("프레임 캡처 실패. 다음 루프로 이동합니다.")
            continue
        
        predicted_label = process_frame(frame_path)
        if predicted_label is not None:
            control_rc_car(predicted_label)
        time.sleep(0.1)  # 루프 간 간격
except KeyboardInterrupt:
    print("실시간 처리 종료.")
