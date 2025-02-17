# Raspberry Pi GPIO 라이브러리와 pynput을 임포트
import RPi.GPIO as GPIO
from time import sleep
from pynput import keyboard

# 핀 번호 설정
ENA = 26         # 모터 속도 제어를 위한 PWM 핀
IN1 = 19         # 모터 방향 제어 핀 1
IN2 = 13         # 모터 방향 제어 핀 2
SERVO_PIN = 18   # 서보모터 제어 핀

# GPIO 설정
GPIO.setmode(GPIO.BCM)             # GPIO 핀 번호를 BCM 모드로 설정
GPIO.setup(ENA, GPIO.OUT)          # ENA 핀을 출력 모드로 설정
GPIO.setup(IN1, GPIO.OUT)          # IN1 핀을 출력 모드로 설정
GPIO.setup(IN2, GPIO.OUT)          # IN2 핀을 출력 모드로 설정
GPIO.setup(SERVO_PIN, GPIO.OUT)    # 서보모터 핀을 출력 모드로 설정

# PWM 객체 생성
pwm_motor = GPIO.PWM(ENA, 100)     # ENA 핀에서 100Hz로 PWM 생성
pwm_motor.start(0)                 # 초기 PWM 듀티 사이클을 0으로 설정

pwm_servo = GPIO.PWM(SERVO_PIN, 50) # 서보모터 핀에서 50Hz로 PWM 생성
pwm_servo.start(0)                 # 초기 서보모터 듀티 사이클을 0으로 설정

# 초기 서보모터 각도 설정
servo_angle = 45

# 모터 상태와 속도를 제어하는 함수
def set_motor(state, speed=0):
    pwm_motor.ChangeDutyCycle(speed)  # 속도를 제어하는 듀티 사이클 설정
    if state == "forward":            # 전진 상태
        GPIO.output(IN1, GPIO.HIGH)   # IN1 HIGH, IN2 LOW로 설정
        GPIO.output(IN2, GPIO.LOW)
    elif state == "backward":         # 후진 상태
        GPIO.output(IN1, GPIO.LOW)    # IN1 LOW, IN2 HIGH로 설정
        GPIO.output(IN2, GPIO.HIGH)
    elif state == "stop":             # 정지 상태
        GPIO.output(IN1, GPIO.LOW)    # IN1 LOW, IN2 LOW로 설정
        GPIO.output(IN2, GPIO.LOW)

# 서보모터 각도를 설정하는 함수
def set_servo_angle(angle):
    # 각도를 0도에서 90도 사이로 제한
    if angle < 0:
        angle = 0
    elif angle > 90:
        angle = 90
    duty = angle / 18 + 2              # 각도를 듀티 사이클로 변환
    GPIO.output(SERVO_PIN, True)      # 서보모터 핀 HIGH
    pwm_servo.ChangeDutyCycle(duty)   # 듀티 사이클 변경
    sleep(0.3)                        # 서보모터가 움직일 시간을 줌
    GPIO.output(SERVO_PIN, False)     # 서보모터 핀 LOW
    pwm_servo.ChangeDutyCycle(0)      # 듀티 사이클 0으로 설정

# 키보드 입력 이벤트 처리 함수
def on_press(key):
    global servo_angle  # 전역 변수로 선언된 servo_angle 사용
    try:
        if key.char == 'w':           # 'w' 키: 전진
            set_motor("forward", 80)
        elif key.char == 's':         # 's' 키: 후진
            set_motor("backward", 80)
        elif key.char == 'x':         # 'x' 키: 정지
            set_motor("stop")
        elif key.char == 'a':         # 'a' 키: 서보모터 각도 감소 (좌회전)
            servo_angle -= 10
            set_servo_angle(servo_angle)
        elif key.char == 'd':         # 'd' 키: 서보모터 각도 증가 (우회전)
            servo_angle += 10
            set_servo_angle(servo_angle)
    except AttributeError:
        pass  # 특수 키 입력 시 무시

# 키보드 리스너를 시작
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 메인 루프
try:
    while True:
        sleep(0.1)  # CPU 사용량을 낮추기 위해 약간 대기
finally:
    pwm_motor.stop()      # 모터 PWM 정지
    pwm_servo.stop()      # 서보모터 PWM 정지
    GPIO.cleanup()        # GPIO 핀 정리
