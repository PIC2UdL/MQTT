import time

import RPi.GPIO as GPIO
import SimpleMFRC522

from .numeric import NumericSensor


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
        self.value = 0.0
        self.flow_acumulative = 0.0
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.lastvalue = 0.0
        self.state = True

    def countPulse(channel):
        self.value = self.value + (0.5/1765)
        if(self.lastvalue == self.value):
            self.state = False
        self.lastvalue = self.value

    def setup(self):
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.countPulse)

        while self.state:
            time.sleep(1)

        self.flow_acumulative += self.value
        GPIO.cleanup()

    def get_acumulative(self):
        return self.flow_acumulative

    def reset_cumulative(self):
        self.flow_acumulative = 0.0
