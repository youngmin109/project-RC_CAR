# Raspberry Pi GPIO 라이브러리와 time 모듈 임포트
import RPi.GPIO as GPIO
from time import sleep

# 모터 상태 상수 정의
STOP = 0       # 모터 정지
FORWARD = 1    # 모터 전진
BACKWARD = 2   # 모터 후진

# GPIO 핀 번호 설정
ENA = 26  # 모터 속도 제어를 위한 PWM 핀
IN1 = 19  # 모터 방향 제어 핀 1 (전진)
IN2 = 13  # 모터 방향 제어 핀 2 (후진)

# GPIO 초기화 및 핀 설정
GPIO.setmode(GPIO.BCM)          # BCM 모드로 GPIO 설정
GPIO.setup(ENA, GPIO.OUT)       # ENA 핀 출력 모드로 설정
GPIO.setup(IN1, GPIO.OUT)       # IN1 핀 출력 모드로 설정
GPIO.setup(IN2, GPIO.OUT)       # IN2 핀 출력 모드로 설정

# PWM 설정
pwm = GPIO.PWM(ENA, 100)        # ENA 핀에서 100Hz로 PWM 생성
pwm.start(0)                    # 초기 듀티 사이클을 0으로 설정 (정지 상태)

# 모터 상태와 속도를 제어하는 함수
def set_motor(state, speed=0):
    if state == FORWARD:  # 전진 상태
        GPIO.output(IN1, GPIO.HIGH)  # IN1 HIGH, IN2 LOW로 설정
        GPIO.output(IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(speed)  # 속도 설정
    elif state == BACKWARD:  # 후진 상태
        GPIO.output(IN1, GPIO.LOW)  # IN1 LOW, IN2 HIGH로 설정
        GPIO.output(IN2, GPIO.HIGH)
        pwm.ChangeDutyCycle(speed)  # 속도 설정
    elif state == STOP:  # 정지 상태
        GPIO.output(IN1, GPIO.LOW)  # IN1 LOW, IN2 LOW로 설정
        GPIO.output(IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(0)  # 속도 0으로 설정 (정지)

# 메인 프로그램
try:
    print("Forward")          # 전진 메시지 출력
    set_motor(FORWARD, 80)    # 모터를 80% 속도로 전진
    sleep(5)                  # 5초 동안 전진

    print("Backward")         # 후진 메시지 출력
    set_motor(BACKWARD, 50)   # 모터를 50% 속도로 후진
    sleep(5)                  # 5초 동안 후진

    print("Stop")             # 정지 메시지 출력
    set_motor(STOP)           # 모터 정지
    sleep(2)                  # 2초 동안 대기

# 프로그램 종료 시 GPIO 및 PWM 정리
finally:
    pwm.stop()                # PWM 정지
    GPIO.cleanup()            # GPIO 설정 초기화
