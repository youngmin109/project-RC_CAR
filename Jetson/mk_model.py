import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# 데이터셋 경로 설정
dataset_dir = "/home/baetani/dataSet"

# 데이터 전처리 변환 설정
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # 이미지 크기 조정
    transforms.ToTensor(),          # Tensor 변환
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # 정규화
])

# 데이터셋 로드
train_dataset = datasets.ImageFolder(root=dataset_dir, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 클래스 개수 확인
num_classes = len(train_dataset.classes)
print(f"클래스 개수: {num_classes}")
print(f"클래스 이름: {train_dataset.classes}")

# CUDA 대신 CPU 설정
device = torch.device("cpu")
print(f"Using device: {device}")

# 사전 훈련된 모델 불러오기 및 수정 (ResNet18)
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(model.fc.in_features, num_classes)  # 분류기 변경
model = model.to(device)

# 손실 함수 및 최적화 알고리즘 설정
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 모델 훈련
num_epochs = 10
train_loss_history = []

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)
    train_loss_history.append(avg_loss)
    print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")

# 훈련된 모델 저장
model_save_path = os.path.expanduser("~/trained_model_cpu.pth")
torch.save(model.state_dict(), model_save_path)
print(f"모델이 저장되었습니다: {model_save_path}")

# 훈련 과정 시각화
plt.plot(range(1, num_epochs + 1), train_loss_history, label='Train Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Trend')
plt.legend()
plt.show()