import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense
from tensorflow.keras.optimizers import Adam

# 데이터 경로 설정
data_dir = '/home/HyoChan/RC_CAR/images'

# 데이터 로드 함수
def load_data(data_dir):
    image_paths = []
    labels = []

    for file_name in os.listdir(data_dir):
        if 'left' in file_name.lower():  # 제목에 'left'가 들어가면
            image_paths.append(os.path.join(data_dir, file_name))
            labels.append(0)  # Left: 0
        elif 'right' in file_name.lower():  # 제목에 'right'가 들어가면
            image_paths.append(os.path.join(data_dir, file_name))
            labels.append(1)  # Right: 1

    images = []
    for image_path in image_paths:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # 흑백으로 읽기
        if image is not None:
            resized = cv2.resize(image, (64, 64))  # 이미지 크기 조정
            images.append(resized / 255.0)  # 정규화

    return np.array(images).reshape(-1, 64, 64, 1), np.array(labels)

# 데이터 불러오기
X_train, y_train = load_data(data_dir)
print(f"데이터 로드 완료: {len(X_train)}개의 이미지")

# 모델 생성 함수
def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 1)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(2, activation='softmax')  # Left(0), Right(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# 모델 생성
model = create_model()
print("모델 생성 완료")

# 모델 학습 함수
def train_model(model, X_train, y_train, epochs=10):
    model.fit(X_train, y_train, validation_split=0.2, epochs=epochs, batch_size=32)
    model.save('/home/HyoChan/RC_CAR/autonomous_car_model.h5')  
    # 효찬 SD카드으로로 교체 
    # 모델 저장
    print("모델 학습 및 저장 완료")

# 모델 학습
train_model(model, X_train, y_train, epochs=10)
