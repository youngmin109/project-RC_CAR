import RPi.GPIO as GPIO
from time import sleep

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    if angle < 0:
        angle = 0
    elif angle > 90:
        angle = 90
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

try:
    set_angle(0)
    sleep(2)
    set_angle(45)
    sleep(2)
    set_angle(90)
    sleep(2)

finally:
    pwm.stop()
    GPIO.cleanup()