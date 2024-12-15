import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import numpy as np
import cv2

# 데이터셋 경로
folder_path = "/home/HyoChan/RC_CAR/images"
left_path = os.path.join(folder_path, "Left")
right_path = os.path.join(folder_path, "Right")
straight_path = os.path.join(folder_path, "Straight")

# 데이터 로드 및 전처리
img_size = (64, 64)  # 이미지 크기

def load_images_from_folder(folder, label):
    images = []
    labels = []
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)  # 흑백 이미지로 읽기
            img = cv2.resize(img, img_size)  # 크기 조정
            images.append(img)
            labels.append(label)
    return images, labels

# 각 방향 데이터 로드
left_images, left_labels = load_images_from_folder(left_path, 0)  # Left: 0
right_images, right_labels = load_images_from_folder(right_path, 1)  # Right: 1
straight_images, straight_labels = load_images_from_folder(straight_path, 2)  # Straight: 2

# 데이터 합치기
images = np.array(left_images + right_images + straight_images)
labels = np.array(left_labels + right_labels + straight_labels)

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
