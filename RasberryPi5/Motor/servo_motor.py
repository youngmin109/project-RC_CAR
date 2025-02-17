import RPi.GPIO as GPIO
import time

# GPIO 핀 설정
servo_pin = 18  # 서보모터 GPIO 핀
dc_motor_pin = 23  # DC 모터 GPIO 핀

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(dc_motor_pin, GPIO.OUT)

# PWM 설정 (서보모터 50Hz, DC 모터 속도 제어)
servo_pwm = GPIO.PWM(servo_pin, 50)  # 서보모터용 50Hz
dc_motor_pwm = GPIO.PWM(dc_motor_pin, 100)  # DC 모터용 100Hz

# PWM 시작
servo_pwm.start(0)
dc_motor_pwm.start(0)

def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 각도에 따른 듀티사이클 계산
    GPIO.output(servo_pin, True)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    servo_pwm.ChangeDutyCycle(0)

def set_dc_motor_speed(speed):
    dc_motor_pwm.ChangeDutyCycle(speed)  # 속도 조절

try:
    while True:
        set_servo_angle(90)  # 서보모터 90도 회전
        time.sleep(2)
        
        set_dc_motor_speed(50)  # DC 모터 50% 속도
        time.sleep(2)

except KeyboardInterrupt:
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()