#!/usr/bin/env python
#-*-coding:utf_8-*-
import ConfigParser
import argparse
import logging
import random
import time

import notifications
import sensors

#

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

parser = argparse.ArgumentParser(description='Receive the arguments for the program')
parser.add_argument('-pin', type=int, default='23', help='Receive the pin of flow sensor')
parser.add_argument('-impn', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for NFC')
parser.add_argument('-impf', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for flow meter')


class nfckeg(object):
    """nfckeg"""

    def __init__(self, pin, impn, impf):
        super(nfckeg, self).__init__()
        self.NFC = None
        self.Flow_meter = None
        self.Relay = None
        self.beer = {}
        self.pin = pin
        self.lastdata_FLOW = 0.0
        self.impn = impn
        self.impf = impf

        self.notify = notifications.MockNotification()
        # self.notify = notifications.TelegramNotification()

    def create_sensors(self):
        NFC_name = "NFC"
        Flow_name = "FLOW"

        if (self.impn == 'mock'):
            self.NFC = sensors.mocksensor.NFCSensor(NFC_name)
        else:
            self.NFC = sensors.realsensor.NFCSensor(NFC_name)

        if (self.impf == 'mock'):
            self.Flow_meter = sensors.mocksensor.FlowSensor(Flow_name)
        else:
            self.Flow_meter = sensors.realsensor.FlowSensor(Flow_name, self.pin)


    def get_state(self):
        self.NFC.setup()
        data_NFC = self.NFC.get_data()

        if( data_NFC != None):
            print 'Relay on'

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
            print 'Relay off'


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

    config = ConfigParser.RawConfigParser()
    args = parser.parse_args()
    try:
        config.read('configuration_file.cfg')
        pin = config.getint('Section1', 'pin')
        imp_n = config.get('Section1', 'NFC_implementation')
        imp_f = config.get('Section1', 'Flow_meter_implementation')

    except:

        config.add_section('Section1')
        config.set('Section1', 'pin', str(args.pin))
        config.set('Section1', 'NFC_implementation', args.impn)
        config.set('Section1', 'Flow_meter_implementation', args.impf)

        with open('configuration_file.cfg', 'wb') as configfile:
            config.write(configfile)

    config.read('configuration_file.cfg')
    pin = config.getint('Section1', 'pin')
    imp_n = config.get('Section1', 'NFC_implementation')
    imp_f = config.get('Section1', 'Flow_meter_implementation')


    random.seed(2)
    NFCKEG = nfckeg(args.pin, args.impn, args.impf)
    NFCKEG.main()
