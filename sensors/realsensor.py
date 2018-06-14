import time

import RPi.GPIO as GPIO
# import SimpleMFRC522
import paho.mqtt.client as mqtt

from .numeric import NumericSensor

'''
class NFCSensor(NumericSensor):
    """NFCSensor class """

    def __init__(self, name):
        super(NFCSensor, self).__init__(name)
        self.value = None

    # Update the value of NFC sensor.
    def setup(self):
        reader = SimpleMFRC522.SimpleMFRC522()

        try:
            id, text = reader.read()
            self.value = id
        finally:
            GPIO.cleanup()

    def get_acumulative(self):
        return "Error"
'''


class Test(NumericSensor):
    def __init__(self, name):
        super(Test, self).__init__(name)
        self.flow_acumulative = 0.0

    # Return the value of cumulative flow.
    def get_cumulative(self):
        return self.flow_acumulative

    def reset_cumulative(self):
        self.flow_acumulative = 0.0


class FlowSensor(NumericSensor):
    """FlowSensor class"""

    def __init__(self, name, pin):
        super(FlowSensor, self).__init__(name)
        self.value = 0.0
        self.pin = pin
        self.state = True
        self.flow_cumulative = 0.0

    def setup(self):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.countPulse)

    def update(self):
        lastvalue = -1
        while True:
            time.sleep(3)
            if lastvalue == self.value:
                self.flow_cumulative += self.value
                break
            lastvalue = self.value

    # Add the values get from flow sensor converting the pulses given in liters with a conversion factor.
    def countPulse(self, channel):
        self.value = self.value + (0.5 / 1765)

    # Return the value of cumulative flow.
    def get_cumulative(self):
        return self.flow_cumulative

    def reset_cumulative(self):
        self.flow_cumulative = 0.0


class ESPFlow(NumericSensor):
    """ESPFlow class"""

    def __init__(self, name, logger):
        super(ESPFlow, self).__init__(name)
        self.logger = logger

    def setup(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("127.0.0.1", 1883, 60)

        client.loop_start()

    # Add the values get from flow sensor converting the pulses given in liters with a conversion factor.
    def countPulse(self, count):
        self.value = count * (0.5 / 1765)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/sensor/FlowSensor")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        self.logger.info('Received {} from topic {} ({})'.format(msg.payload, msg.topic, self.name))
        self.countPulse(float(msg.payload))
