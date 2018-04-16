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
        self.lastvalue = 0.0
        self.state = True

    def countPulse(self, channel):
        self.value = self.value + (0.5/1765)

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.countPulse)

        while True:
            time.sleep(3)
            if(self.lastvalue == self.value):
                self.flow_acumulative += self.value
                break
            self.lastvalue = self.value

        GPIO.cleanup()

    def get_acumulative(self):
        return self.flow_acumulative

    def reset_cumulative(self):
        self.flow_acumulative = 0.0
