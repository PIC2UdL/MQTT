#!/usr/bin/env python
#-*-coding:utf_8-*-
import time
import notifications
import sensors
import random
import argparse
import logging

#Create Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Define the formatter
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

#Create the file to save the results
file_handler = logging.FileHandler('Difference.log')
file_handler.setFormatter(formatter)

#Add file and stream in the logging already created before
logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description= 'Receive the arguments for the program')
parser.add_argument('-ip', type = str, default = 'localhost', help = 'Receive the ip_address of the user')
parser.add_argument('-p', type = str, default = '10000', help = 'Receive the port to communicate with the user')
parser.add_argument('-pin', type = int, default = '23', help = 'Receive the pin of flow sensor')
parser.add_argument('-imp', type = str, default = 'mock', help = 'Choose between mock or real implementation')

class nfckeg(object):
    """nfckeg"""
    def __init__(self, ip_address, port, pin, imp):
        super(nfckeg, self).__init__()
        self.NFC = None
        self.Flow_meter = None
        self.Relay = None
        self.beer = {}
        self.pin = pin
        self.user = (ip_address, port)
        self.lastdata_FLOW = 0.0
        self.imp = imp


        self.notify = notifications.MockNotification()
        #self.notify = notifications.TelegramNotification()

    def create_sensors(self):
        NFC_name = "NFC"
        Flow_name = "FLOW"
        Relay_name = "RELAY"
        #MockSensor
        if (self.imp == 'mock'):
            self.NFC = sensors.mocksensor.NFCSensor(NFC_name)
            self.Flow_meter = sensors.mocksensor.FlowSensor(Flow_name)
            self.Relay = sensors.mocksensor.RelaySensor(Relay_name)
        #RealSensor
        else:
            self.NFC= sensors.realsensor.NFCSensor(NFC_name)
            self.Flow_meter = sensors.realsensor.FlowSensor(Flow_name, self.pin)
            self.Relay = sensors.realsensor.RelaySensor(Relay_name)
        pass


    def get_state(self):
        self.NFC.setup()
        data_NFC = self.NFC.get_data()

        if( data_NFC != None):
            self.Relay.setup('on')

            while True:
                self.Flow_meter.setup()
                data_FLOW = self.Flow_meter.get_data()

                if(data_FLOW != 0):
                    self.beer[data_NFC] = self.beer.get(data_NFC, 0) + data_FLOW
                    if(self.lastdata_FLOW != 0):
                        difference = data_FLOW - self.lastdata_FLOW
                        logger.debug('Difference: {}'.format(difference))
                    self.lastdata_FLOW = data_FLOW
                    break
            self.Relay.setup('off')


    def main(self):
        self.create_sensors()

        while True:
            self.get_state()

            print ("This is the acumulative of beer: {} Litro(s)".format(self.Flow_meter.get_acumulative()))

            for tarjetas in self.beer:
                message = ('{}: {}'.format(tarjetas, self.beer[tarjetas]))
                print message
                #self.notify.notify(self.user, message)
                #self.notify.broadcast(message)
            time.sleep(1)
        pass

if __name__=='__main__':
    args = parser.parse_args()
    random.seed(2)
    NFCKEG = nfckeg(args.ip, args.p, args.pin, args.imp)
    NFCKEG.main()
