from .binary import BinarySensor
from .numeric import NumericSensor
import RPi.GPIO as GPIO
import SimpleMFRC522
import time, sys


class NFCSensor(NumericSensor):
    """NFCSensor"""
    def __init__(self, name):
        super(NFCSensor, self).__init__(name)
        self.value = None

    def setup(self):
        reader = SimpleMFRC522.SimpleMFRC522()

        try:
                id, text = reader.read()
                self.value = id
        finally:
                GPIO.cleanup()
        pass

    def get_acumulative(self):
        return "Error"
        pass

    def reset_cumulative(self):
        pass

class FlowSensor(NumericSensor):
    """FlowSensor"""
    def __init__(self, name, pin):
        super(FlowSensor, self).__init__(name)
        self.value = 0
        self.flow_acumulative = 0.0
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.lastvalue = 0
        self.state = True

    def countPulse(channel):
        self.value = self.value + 0.5/1765
        if(self.lastvalue == self.value):
            self.state = False
        self.lastvalue = self.value

    def setup(self):
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.countPulse)
        while self.state:
            time.sleep(1)

        if (self.value != None):
            self.flow_acumulative += self.value
        GPIO.cleanup()

    def get_acumulative(self):
            if (self.flow_acumulative != 0.0):
                return self.flow_acumulative
            return "Error"
            pass

    def reset_cumulative(self):
            self.flow_acumulative = 0.0
            pass

class RelaySensor(BinarySensor):
    """RelaySensor"""
    def __init__(self, name):
        super(RelaySensor, self).__init__(name)

    def setup(self, status):
        if (status == 'on'):
            self.state = 1
        else:
            self.state = 0
