import cv2
import time
import numpy as np
import os

# GPIO 핀 설정
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

# 카메라 설정
class MyCamera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.camera = cv2.VideoCapture(0)  # 0번 카메라 사용
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def isOpened(self):
        return self.camera.isOpened()

    def read(self):
        ret, frame = self.camera.read()
        return ret, frame

    def release(self):
        self.camera.release()

# 모터 관련 설정 함수(placeholder)
def motor_go(speed):
    print(f"모터 전진, 속도: {speed}")

def motor_stop():
    print("모터 정지")

def motor_left(speed):
    print(f"모터 왼쪽 회전, 속도: {speed}")

def motor_right(speed):
    print(f"모터 오른쪽 회전, 속도: {speed}")

# 메인 함수
def main():
    camera = MyCamera(640, 480)
    filepath = "/home/pi/Image/"  # 저장될 위치
    os.makedirs(filepath, exist_ok=True)  # 저장 경로 생성
    i = 0
    carState = "stop"
    speedSet = 0.5

    while camera.isOpened():
        keyValue = cv2.waitKey(10)

        if keyValue == ord('q'):  # 'q'를 누르면 종료
            break
        elif keyValue == 82:  # 위쪽 방향키: 전진
            print("go")
            carState = "go"
            motor_go(speedSet)
        elif keyValue == 84:  # 아래쪽 방향키: 정지
            print("stop")
            carState = "stop"
            motor_stop()
        elif keyValue == 81:  # 왼쪽 방향키: 좌회전
            print("left")
            carState = "left"
            motor_left(speedSet)
        elif keyValue == 83:  # 오른쪽 방향키: 우회전
            print("right")
            carState = "right"
            motor_right(speedSet)

        _, image = camera.read()
        if image is not None:
            image = cv2.flip(image, -1)  # 이미지 좌우 반전
            cv2.imshow('Original', image)

            # 전처리: 높이를 절반으로 잘라 저장
            height, _, _ = image.shape
            save_image = image[int(height / 2):, :, :]
            save_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2YUV)
            save_image = cv2.GaussianBlur(save_image, (3, 3), 0)
            save_image = cv2.resize(save_image, (200, 66))

            cv2.imshow('Save', save_image)

            # 상태에 따라 이미지 저장
            if carState == "left":
                cv2.imwrite(f"{filepath}{i:05d}_45d.png", save_image)
                i += 1
            elif carState == "right":
                cv2.imwrite(f"{filepath}{i:05d}_135d.png", save_image)
                i += 1
            elif carState == "go":
                cv2.imwrite(f"{filepath}{i:05d}_90d.png", save_image)
                i += 1

    camera.release()
    cv2.destroyAllWindows()

# 실행
if __name__ == "__main__":
    main()