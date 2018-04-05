from .binary import BinarySensor
from .numeric import NumericSensor
from sensorslibrary import Sensorslibrary

#import Adafruit_DHT
#import RPi.GPIO as GPIO

class NFCSensor(NumericSensor):
    """NFCSensor"""
    def __init__(self, name):
        super(NFCSensor, self).__init__(name)
        self.value = None

    def setup(self):
        try:
            id = Sensorslibrary.nfc()
            self.value = id
        except:
            print "Error!"
        pass

    def get_acumulative(self):
        return "Error"
        pass

    def reset_cumulative(self):
        pass

class FlowSensor(NumericSensor):
    """FlowSensor"""
    def __init__(self, name):
        super(FlowSensor, self).__init__(name)
        self.value = None
        self.flow_acumulative = 0.0

    def setup(self):
            self.value = Sensorslibrary.flow()
            if (self.value != None):
                self.flow_acumulative += self.value

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
