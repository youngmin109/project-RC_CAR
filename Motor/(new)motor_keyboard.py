import RPi.GPIO as GPIO
from time import sleep
from pynput import keyboard

ENA = 26
IN1 = 19
IN2 = 13
SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm_motor = GPIO.PWM(ENA, 100)
pwm_motor.start(0)

pwm_servo = GPIO.PWM(SERVO_PIN, 50)
pwm_servo.start(0)

servo_angle = 45

def set_motor(state, speed=0):
    pwm_motor.ChangeDutyCycle(speed)
    if state == "forward":
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif state == "backward":
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    elif state == "stop":
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)

def set_servo_angle(angle):
    if angle < 0:
        angle = 0
    elif angle > 90:
        angle = 90
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm_servo.ChangeDutyCycle(duty)
    sleep(0.3)
    GPIO.output(SERVO_PIN, False)
    pwm_servo.ChangeDutyCycle(0)

def on_press(key):
    global servo_angle
    try:
        if key.char == 'w':
            set_motor("forward", 80)
        elif key.char == 's':
            set_motor("backward", 80)
        elif key.char == 'x':
            set_motor("stop")
        elif key.char == 'a':
            servo_angle -= 10
            set_servo_angle(servo_angle)
        elif key.char == 'd':
            servo_angle += 10
            set_servo_angle(servo_angle)
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
    while True:
        sleep(0.1)
finally:
    pwm_motor.stop()
    pwm_servo.stop()
    GPIO.cleanup()ddaadaaaaddddwwsssasxx
