import time
import pygame
from gpiozero import Motor, PWMOutputDevice
from adafruit_servokit import ServoKit

# Pygame 초기화
pygame.init()
screen = pygame.display.set_mode((300, 300))

# 16채널 PCA9685 모듈에 서보모터 연결
kit = ServoKit(channels=16)  # PCA9685에 16채널 서보모터 연결

# 라즈베리파이 GPIO 핀 설정 (DC 모터용)
dc_motor = Motor(forward=17, backward=27)  # DC 모터 전진과 후진 핀 설정
dc_speed = PWMOutputDevice(23)  # ENA 핀에 PWM 신호를 보낼 핀 설정

# 초기 각도와 속도 설정
servo_angle = 90  # 서보모터 기본 각도 (0~180도 사이)
dc_motor_speed = 0  # DC 모터 기본 속도 (0~1)

def set_servo_angle(angle):
    if 0 <= angle <= 180:
        kit.servo[0].angle = angle  # PCA9685의 0번 채널 서보모터 제어
        time.sleep(0.1)

def set_dc_motor_speed(speed):
    if speed > 0:
        dc_motor.forward(speed)
    elif speed < 0:
        dc_motor.backward(abs(speed))
    else:
        dc_motor.stop()

try:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # 키보드 입력 감지
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # 서보모터 왼쪽으로 (10도씩 감소)
                    servo_angle -= 10
                    if servo_angle < 0:
                        servo_angle = 0  # 각도 하한
                    set_servo_angle(servo_angle)
                    print(f"서보모터 각도: {servo_angle}도")

                elif event.key == pygame.K_RIGHT:
                    # 서보모터 오른쪽으로 (10도씩 증가)
                    servo_angle += 10
                    if servo_angle > 180:
                        servo_angle = 180  # 각도 상한
                    set_servo_angle(servo_angle)
                    print(f"서보모터 각도: {servo_angle}도")

                elif event.key == pygame.K_UP:
                    # DC 모터 속도 증가
                    dc_motor_speed += 0.1
                    if dc_motor_speed > 1:
                        dc_motor_speed = 1  # 속도 상한 (1.0 = 100%)
                    set_dc_motor_speed(dc_motor_speed)
                    print(f"DC 모터 속도: {dc_motor_speed * 100}%")

                elif event.key == pygame.K_DOWN:
                    # DC 모터 속도 감소
                    dc_motor_speed -= 0.1
                    if dc_motor_speed < -1:
                        dc_motor_speed = -1  # 속도 하한 (역방향)
                    set_dc_motor_speed(dc_motor_speed)
                    print(f"DC 모터 속도: {dc_motor_speed * 100}%")

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    pygame.quit()