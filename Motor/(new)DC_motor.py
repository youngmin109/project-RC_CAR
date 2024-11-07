import RPi.GPIO as GPIO
from time import sleep

STOP = 0
FORWARD = 1
BACKWARD = 2


ENA = 26  # 
IN1 = 19  # 
IN2 = 13  # 

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# PWM 
pwm = GPIO.PWM(ENA, 100)
pwm.start(0)  

# 
def set_motor(state, speed=0):
    if state == FORWARD:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(speed)  
    elif state == BACKWARD:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        pwm.ChangeDutyCycle(speed) 
    elif state == STOP:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(0) 


try:
   
    print("Forward")
    set_motor(FORWARD, 80)
    sleep(5)

    
    print("Backward")
    set_motor(BACKWARD, 50)
    sleep(5)

   
    print("Stop")
    set_motor(STOP)
    sleep(2)

finally:
    
    pwm.stop()
    GPIO.cleanup()