from sensorslibrary import Sensorslibrary

from .numeric import NumericSensor


class NFCSensor(NumericSensor):
    """NFCSensor"""

    def __init__(self, name):
        super(NFCSensor, self).__init__(name)
        self.value = None

    def setup(self):
        self.value = Sensorslibrary.nfc()

    def get_cumulative(self):
        raise NotImplementedError()


class FlowSensor(NumericSensor):
    """FlowSensor"""

    def __init__(self, name):
        super(FlowSensor, self).__init__(name)
        self.flow_cumulative = 0.0

    def update(self):
        self.value = Sensorslibrary.flow()
        self.flow_cumulative += self.value

    def get_cumulative(self):
        return self.flow_cumulative

    def reset_cumulative(self):
        self.flow_cumulative = 0.0
