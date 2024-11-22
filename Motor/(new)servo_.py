# Raspberry Pi GPIO 라이브러리와 time 모듈 임포트
import RPi.GPIO as GPIO
from time import sleep

# 서보모터를 제어할 GPIO 핀 번호
SERVO_PIN = 18

# GPIO 설정
GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 체계 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)  # 서보모터 핀을 출력 모드로 설정

# PWM 생성 (서보모터의 제어 주파수는 50Hz)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)  # 초기 듀티 사이클을 0으로 설정 (모터 정지 상태)

# 서보모터 각도를 설정하는 함수
def set_angle(angle):
    # 각도를 0° ~ 90° 사이로 제한
    if angle < 0:
        angle = 0
    elif angle > 90:
        angle = 90
    
    # 각도를 듀티 사이클로 변환 (각도에 따라 서보모터 제어)
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)  # 신호를 HIGH로 설정
    pwm.ChangeDutyCycle(duty)  # 듀티 사이클 변경
    sleep(1)  # 서보모터가 이동할 시간을 줌
    GPIO.output(SERVO_PIN, False)  # 신호를 LOW로 설정
    pwm.ChangeDutyCycle(0)  # 듀티 사이클을 0으로 설정 (모터 대기 상태)

# 메인 프로그램 실행
try:
    # 서보모터를 0°, 45°, 90°로 회전시키며 각 상태에서 2초 대기
    set_angle(0)  # 0°로 설정
    sleep(2)  # 2초 대기
    set_angle(45)  # 45°로 설정
    sleep(2)  # 2초 대기
    set_angle(90)  # 90°로 설정
    sleep(2)  # 2초 대기

# 프로그램 종료 시 GPIO와 PWM 정리
finally:
    pwm.stop()  # PWM 정지
    GPIO.cleanup()  # GPIO 설정 초기화
