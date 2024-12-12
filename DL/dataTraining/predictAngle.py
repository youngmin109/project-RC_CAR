import mycamera  # 사용자 정의 카메라 모듈 가져오기
import cv2  # OpenCV를 사용한 이미지 처리
import numpy as np  # 행렬 연산과 배열 처리를 위한 라이브러리
import tensorflow as tf  # 딥러닝 모델 사용
from tensorflow.keras.models import load_model  # 저장된 모델 불러오기

# 이미지 전처리 함수
def img_preprocess(image):
    # 이미지 크기 정보 가져오기
    height, _, _ = image.shape
    # 이미지 절반 자르기 (상단 부분 제거)
    image = image[int(height/2):, :, :]
    # BGR 이미지를 YUV 이미지로 변환
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    # 가우시안 블러링을 적용해 노이즈 제거
    image = cv2.GaussianBlur(image, (3, 3), 0)
    # 이미지를 200x66 크기로 리사이즈
    image = cv2.resize(image, (200, 66))
    # 픽셀 값을 255로 나눠서 정규화
    image = image / 255
    return image

# 메인 함수
def main():
    # 사용자 정의 카메라 설정 (해상도: 640x480)
    camera = mycamera.MyPiCamera(640, 480)
    # 학습된 모델 경로
    model_path = '/home/pi/AI_CAR/model/lane_navigation_final.h5'
    # 모델 불러오기
    model = load_model(model_path)

    # 초기 차량 상태 설정
    carState = "stop"

    # 카메라가 열려 있는 동안 루프 실행
    while camera.isOpened():
        # 키보드 입력 대기
        keyValue = cv2.waitKey(1)

        # 'q' 키를 누르면 루프 종료
        if keyValue == ord('q'):
            break

        # 카메라에서 이미지 읽기
        _, image = camera.read()
        # 이미지를 좌우 반전
        image = cv2.flip(image, -1)
        # 원본 이미지 표시
        cv2.imshow('Original', image)

        # 이미지 전처리
        preprocessed = img_preprocess(image)
        # 전처리된 이미지 표시
        cv2.imshow('pre', preprocessed)

        # 전처리된 이미지를 numpy 배열로 변환
        X = np.asarray([preprocessed])
        # 학습된 모델로 각도 예측
        steering_angle = int(model.predict(X)[0])
        # 예측된 각도 출력
        print("predict angle:", steering_angle)

    # 모든 창 닫기
    cv2.destroyAllWindows()

# 메인 함수 실행
if __name__ == "__main__":
    main()