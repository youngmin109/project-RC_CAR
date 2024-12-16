import RPi.GPIO as GPIO  # 라즈베리파이 GPIO 라이브러리
import time
import cv2  # OpenCV 사용 예시
import os

# GPIO 핀 설정
SERVO_PIN = 18  # 서보모터 핀 번호 (PWM 제어)
MOTOR_FORWARD = 23  # 모터 전진 핀
MOTOR_STOP = 24  # 모터 정지 핀
MOTOR_LEFT = 25  # 좌회전 핀
MOTOR_RIGHT = 8  # 우회전 핀

# GPIO 설정
GPIO.setmode(GPIO.BCM)  # BCM 모드 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup([MOTOR_FORWARD, MOTOR_STOP, MOTOR_LEFT, MOTOR_RIGHT], GPIO.OUT)

# PWM 설정
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM 신호
pwm.start(0)  # 초기 듀티사이클 0%

# 초기값 설정
angle = 90  # 초기 서보모터 각도
step = 5    # 각도 변경 단위
speedSet = 50  # 속도 값
current_time = time.time()

# 이미지 저장 폴더 설정
if not os.path.exists("images"):
    os.makedirs("images")

# 서보모터 각도 설정 함수
def set_angle(angle):
    duty = angle / 18 + 2  # 듀티 사이클 계산 (0도 ~ 180도 범위)
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  # 동작 대기 시간
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

# 모터 제어 함수
def motor_go():
    GPIO.output(MOTOR_FORWARD, GPIO.HIGH)
    GPIO.output([MOTOR_STOP, MOTOR_LEFT, MOTOR_RIGHT], GPIO.LOW)
    print("Motor: Forward")

def motor_stop():
    GPIO.output([MOTOR_FORWARD, MOTOR_STOP, MOTOR_LEFT, MOTOR_RIGHT], GPIO.LOW)
    print("Motor: Stop")

def motor_turn_left():
    GPIO.output(MOTOR_LEFT, GPIO.HIGH)
    GPIO.output([MOTOR_FORWARD, MOTOR_STOP, MOTOR_RIGHT], GPIO.LOW)
    print("Motor: Turn Left")

def motor_turn_right():
    GPIO.output(MOTOR_RIGHT, GPIO.HIGH)
    GPIO.output([MOTOR_FORWARD, MOTOR_STOP, MOTOR_LEFT], GPIO.LOW)
    print("Motor: Turn Right")

# 이미지 저장 함수
def save_image(state_name):
    img_name = f"images/{int(time.time())}_{state_name}.jpg"
    img = camera.capture()  # 이미지 캡처 함수 (카메라 모듈에 맞게 수정 필요)
    cv2.imwrite(img_name, img)
    print(f"Saved: {img_name}")

# 메인 루프
try:
    while True:
        keyValue = cv2.waitKey(0)  # 키 입력 대기

        if keyValue == ord('q'):  # 'q' 종료
            break

        elif keyValue == 81:  # 왼쪽 방향키: 좌회전
            if angle > 5:
                angle -= step
            set_angle(angle)
            motor_turn_left()
            print(f"Left: {angle}")

        elif keyValue == 83:  # 오른쪽 방향키: 우회전
            if angle < 175:
                angle += step
            set_angle(angle)
            motor_turn_right()
            print(f"Right: {angle}")

        elif keyValue == ord('z'):  # 'z' 키: 초기화 (90도)
            while angle < 90:  # 왼쪽에서 돌아올 때
                angle += step
                set_angle(angle)
                time.sleep(0.05)
            while angle > 90:  # 오른쪽에서 돌아올 때
                angle -= step
                set_angle(angle)
                time.sleep(0.05)
            motor_stop()
            save_image("Straight")
            print("Straight: 90")

        elif keyValue == 82:  # 위쪽 방향키: 전진
            motor_go()

        elif keyValue == 84:  # 아래쪽 방향키: 정지
            motor_stop()

        else:
            print("Invalid Key")

except KeyboardInterrupt:
    print("Program Stopped by User")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO Cleaned Up")
