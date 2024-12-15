import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import numpy as np
import cv2

# 데이터셋 경로
folder_path = "/home/pi/RC_CAR/images"

# 데이터 로드 및 전처리
img_size = (64, 64)  # 이미지 크기

def load_images(folder, label_keyword):
    images = []
    labels = []
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            if label_keyword.lower() in filename.lower():
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)  # 흑백 이미지로 읽기
                img = cv2.resize(img, img_size)  # 크기 조정
                images.append(img)
                labels.append(label_keyword)
    return images, labels

# 각 방향 데이터 로드
left_images, left_labels = load_images(folder_path, "left")  # Left: 0
right_images, right_labels = load_images(folder_path, "right")  # Right: 1
straight_images, straight_labels = load_images(folder_path, "straight")  # Straight: 2

# 데이터 합치기
images = np.array(left_images + right_images + straight_images)
labels = np.array([0] * len(left_labels) + [1] * len(right_labels) + [2] * len(straight_labels))

# 정규화
images = images / 255.0
images = images.reshape(-1, img_size[0], img_size[1], 1)  # 채널 추가

# 데이터셋 분리
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.3, random_state=42)

# 모델 정의
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(img_size[0], img_size[1], 1)),
    MaxPooling2D((2, 2)),
    Dropout(0.25),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Dropout(0.25),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(3, activation='softmax')  # 3개의 클래스 (Left, Right, Straight)
])

# 모델 컴파일
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 모델 학습
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), batch_size=32)

# 모델 저장
model.save("direction_classifier.h5")

# 결과 출력
loss, accuracy = model.evaluate(X_test, y_test)
print(f"테스트 손실: {loss}")
print(f"테스트 정확도: {accuracy}")

# RC카 제어 코드
import time

def initialize_servo():
    # 초기 서보모터 값을 30도로 설정
    initial_angle = 30
    print(f"Initializing servo motor to {initial_angle} degrees")
    # 실제 서보모터 초기화 로직 (GPIO 제어 또는 시리얼 통신 등)
    # send_to_servo(initial_angle)

initialize_servo()

def control_rc_car(predicted_label):
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

# 모델 예측 및 RC카 제어 예제
# 테스트 이미지 불러오기 및 예측
sample_image = X_test[0]  # 테스트 데이터 중 하나
sample_image = np.expand_dims(sample_image, axis=0)  # 배치 차원 추가
predicted_label = np.argmax(model.predict(sample_image))

# RC카 제어 함수 호출
control_rc_car(predicted_label)
