import os  # 파일 및 디렉토리 작업을 위한 os 라이브러리
import torch  # PyTorch 라이브러리
import torch.nn as nn  # 신경망 관련 모듈
import torch.optim as optim  # 최적화 알고리즘 모듈
from torchvision import datasets, transforms, models  # torchvision을 이용한 데이터셋 및 모델 사용
from torch.utils.data import DataLoader  # 데이터 로딩을 위한 DataLoader
import matplotlib.pyplot as plt  # 훈련 결과 시각화를 위한 라이브러리

# 데이터셋이 저장된 디렉토리 경로 설정
dataset_dir = "/home/baetani/dataSet"

# 이미지 전처리를 위한 변환(transform) 설정
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # 모든 이미지를 224x224 크기로 조정 (ResNet의 입력 크기)
    transforms.ToTensor(),          # 이미지를 Tensor 형식으로 변환 (PyTorch에서 사용 가능하도록 함)
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # 정규화 (픽셀 값을 [-1, 1] 범위로 조정)
])

# ImageFolder를 이용해 데이터셋을 로드 (폴더 구조에 따라 자동으로 라벨 지정)
train_dataset = datasets.ImageFolder(root=dataset_dir, transform=transform)

# DataLoader를 사용해 배치 단위로 데이터를 로드
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 데이터셋의 클래스 개수 확인
num_classes = len(train_dataset.classes)
print(f"클래스 개수: {num_classes}")  # 클래스 개수 출력
print(f"클래스 이름: {train_dataset.classes}")  # 클래스 이름 출력

# 학습에 사용할 디바이스 설정 (CPU 사용)
device = torch.device("cpu")  # GPU가 아닌 CPU에서 실행하도록 설정
print(f"Using device: {device}")  # 사용 중인 디바이스 출력

# 사전 훈련된 ResNet18 모델 로드 (ImageNet으로 사전 학습됨)
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# ResNet의 최종 분류기 부분(fc layer)을 데이터셋 클래스 수에 맞게 수정
model.fc = nn.Linear(model.fc.in_features, num_classes)

# 모델을 지정된 디바이스로 이동 (CPU에서 실행)
model = model.to(device)

# 손실 함수 (CrossEntropyLoss: 다중 클래스 분류에서 사용)
criterion = nn.CrossEntropyLoss()

# Adam 최적화 알고리즘 설정 (학습률: 0.001)
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 모델 훈련 설정
num_epochs = 10  # 총 10번의 학습 반복
train_loss_history = []  # 학습 과정에서의 손실(loss) 기록 저장 리스트

# 에포크(epochs) 단위로 학습 진행
for epoch in range(num_epochs):
    model.train()  # 모델을 학습 모드로 설정
    running_loss = 0.0  # 에포크별 손실 합 초기화

    # 배치 단위 학습 루프
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)  # 데이터를 CPU로 이동
        
        optimizer.zero_grad()  # 기울기(gradient) 초기화 (이전 배치의 기울기 제거)
        outputs = model(images)  # 모델을 통해 예측값 출력
        loss = criterion(outputs, labels)  # 손실 계산 (예측값과 실제 라벨 비교)
        loss.backward()  # 역전파 수행 (기울기 계산)
        optimizer.step()  # 모델 가중치 업데이트

        running_loss += loss.item()  # 배치별 손실을 합산

    # 에포크별 평균 손실 계산
    avg_loss = running_loss / len(train_loader)
    train_loss_history.append(avg_loss)  # 손실 기록 저장
    print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")  # 진행 상태 출력

# 훈련된 모델 저장 (CPU 전용 모델로 저장)
model_save_path = os.path.expanduser("~/trained_model_cpu.pth")  # 모델 저장 경로 지정
torch.save(model.state_dict(), model_save_path)  # 모델의 가중치(state_dict) 저장
print(f"모델이 저장되었습니다: {model_save_path}")  # 저장 완료 메시지 출력

# 훈련 과정 시각화 (손실 값 그래프)
plt.plot(range(1, num_epochs + 1), train_loss_history, label='Train Loss')  # 에포크별 손실 값 플롯
plt.xlabel('Epochs')  # x축 레이블 설정
plt.ylabel('Loss')  # y축 레이블 설정
plt.title('Training Loss Trend')  # 그래프 제목 설정
plt.legend()  # 범례 표시
plt.show()  # 그래프 출력
