#!/usr/bin/env python
# -*-coding:utf_8-*-
import ConfigParser
import argparse
import logging
import random
import sys
import time

import notifications
import sensors

#

# Create Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define the formatter
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

# Create the file to save the results
file_handler = logging.FileHandler('Difference.log')
file_handler.setFormatter(formatter)

# Add file and stream in the logging already created before
logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description='Receive the arguments for the program')
parser.add_argument('-impn', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for NFC')
parser.add_argument('-impf', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for flow meter')
parser.add_argument('-f', type=str, default='template.cfg',
                    help='Configfile')


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

    def is_mock(self, item):
        return item == 'mock'

    def get_state(self):
        self.NFC.setup()
        data_NFC = self.NFC.get_data()

        if (data_NFC != None):
            print 'Relay on'

            while True:
                self.Flow_meter.setup()
                data_FLOW = self.Flow_meter.get_data()

                if (data_FLOW != 0):
                    self.beer[data_NFC] = self.beer.get(data_NFC, 0) + data_FLOW
                    if (self.lastdata_FLOW != 0):
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
                # self.notify.notify(self.user, message)
                # self.notify.broadcast(message)
            time.sleep(1)
        pass


def check_cfg(file_name):
    import os.path
    config = crear_plantilla()
    if os.path.isfile(file_name):
        read_cfg(file_name, config)
    else:
        write_config(config)
        logger.error('Config file {} not found. Update the new template: '.format(file_name))
        sys.exit()
    return config


def get_value(config, section, option):
    return config.getint(section, option)


def read_cfg(file_name, config):
    config.read(file_name)
    write_config(config, file_name)
    remaining = get_remaining(config)
    if len(remaining) != 0:
        for section, option in remaining:
            logger.error('Fill option {} in section {}.Update file {}'.format(option, section, file_name))
        sys.exit()


def get_remaining(config):
    remaining = []
    for k, v in config._sections.items():
        for k1, v1 in v.items():
            if v1 == '':
                remaining.append((k, k1))
    return remaining


def crear_plantilla():
    config = ConfigParser.RawConfigParser()
    config.add_section('Section1')
    config.set('Section1', 'pin', '')
    config.add_section('Notifications')
    config.set('Notifications', 'Token', '')
    config.set('Notifications', 'Chat_id', '')
    return config


def write_config(config, file_name='template.cfg'):
    with open(file_name, 'wb') as configfile:
        config.write(configfile)


def instance_objects():
    pass


if __name__ == '__main__':
    args = parser.parse_args()
    config = check_cfg(args.f)
    # instance_objects()
    pin = get_value(config, 'Section1', 'pin')
    random.seed(2)
    NFCKEG = nfckeg(pin, args.impn, args.impf)
    NFCKEG.main()
