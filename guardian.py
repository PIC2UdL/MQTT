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
parser.add_argument('-nfc', type = str, help = 'Receive the name of NFC Sensor')
parser.add_argument('-flow', type = str, help = 'Receive the name of Flow Sensor')
parser.add_argument('-relay', type = str, help = 'Receive the name of Relay Sensor')
parser.add_argument('-ip', type = str, help = 'Receive the ip_address of the user')
parser.add_argument('-p', type = str, help = 'Receive the port to communicate with the user')

class Guardian(object):
    """HomeGuardian is a security system for python"""
    def __init__(self, ip_address, port, file):
        super(Guardian, self).__init__()
        self.NFC = None
        self.Flow_meter = None
        self.Relay = None
        self.beer = {}
        self.beer["Tarjetas"] = {}
        self.user = (ip_address, port)
        self.file = file
        self.lastdata_FLOW = 0.0

        self.notify = notifications.MockNotification()
        #self.notify = notifications.TelegramNotification()

    def create_sensors(self, NFC, Flowmeter, Relay):
        self.NFC = sensors.mocksensor.NFCSensor(NFC)
        self.Flow_meter = sensors.mocksensor.FlowSensor(Flowmeter)
        self.Relay = sensors.mocksensor.RelaySensor(Relay)
        pass


    def get_state(self):
        #update
        data_NFC = self.NFC.get_data()
        if( data_NFC == None):
            self.NFC.setup()
        else:
            print data_NFC
            self.Relay.setup('on')
            while True:
                self.Flow_meter.setup()
                data_FLOW = self.Flow_meter.get_data()
                print data_FLOW
                if(data_FLOW != None):
                    self.beer["Tarjetas"][data_NFC] = self.beer['Tarjetas'].get(data_NFC, 0) + data_FLOW
                    difference = data_FLOW - self.lastdata_FLOW
                    logger.debug('Difference: {}'.format(difference))
                    self.lastdata_FLOW = data_FLOW
                    break

        self.Relay.setup('off')

    def main(self):
        while True:
            self.get_state()

            print ("This is the acumulative of beer: {} Litro(s)".format(self.Flow_meter.get_acumulative()))

            for tarjetas in self.beer['Tarjetas']:
                message = ('{}: {}'.format(tarjetas, self.beer['Tarjetas'][tarjetas]))
                print message
                #self.notify.notify(self.user, message)
                #self.notify.broadcast(message)

            time.sleep(1)
        pass

if __name__=='__main__':
    args = parser.parse_args()
    NFC_name = args.nfc
    Flow_name = args.flow
    Relay = args.relay
    ip_address = args.ip
    port = args.p
    file = args.f
    if (ip_address == None):
        ip_address = 'localhost'
    if (port == None):
        port = 10000

    random.seed(1)
    guardian = Guardian(ip_address, port, file)
    guardian.create_sensors(NFC_name, Flow_name, Relay)
    guardian.main()
