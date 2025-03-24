### 캡스톤디자인 RC카 제작 프로젝트 (계속 업데이트 중)
This is a collaborative project for building an autonomous RC car.

- **Rasberry Pi5** : 2024.10.1 ~ 2024.12.16 (X)
- **Jetson nano** : 2024.12.21 ~ 2025.1.26 (O)

**데이터 준비**
- Input data = image  
- Output data = servo Angle <br>

**데이터 처리 과정**
1. 훈련데이터와 검증데이터를 먼저 나눈다. -> 일반화 검증
2. 각각의 클래스 마다 데이터 개수를 맞춰줌 -> 오버샘플링 & UnderSampling  <br>
Match the number of data for each class -> OverSampling & UnderSampling
3. 
Features -> 50, 65, 80, 105, 120

#### **Failed Model**
![Failed Model](https://github.com/youngmin109/RC_CAR/blob/main/IMAGE/training_metrics_cpu(ModelA).png)

#### **Succesed Model**
![Succesed Model](https://github.com/youngmin109/RC_CAR/blob/main/IMAGE/training_metrics_cpu(ModelB).png)
