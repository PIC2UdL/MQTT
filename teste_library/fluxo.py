import RPi.GPIO as GPIO
import time, sys

FLOW_SENSOR = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

global count
count = 0

def countPulse(channel):
    global count

    count = count + 0.5/1765    
    print count


if __name__ == '__main__':
    GPIO.add_event_detect(FLOW_SENSOR, GPIO.RISING, callback=countPulse)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\ncaughtkeyboardinterrupt!, bye"
            GPIO.cleanup()
            sys.exit()
