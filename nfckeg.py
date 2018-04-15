#!/usr/bin/env python
# -*-coding:utf_8-*-
import ConfigParser
import argparse
import logging
import random
import sys
import time

import notification
import sensors

# Create Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define the formatter
formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
console_formatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")

# Create the file to save the results
file_handler = logging.FileHandler('AdvancedLogg.log')
file_handler.setFormatter(formatter)

# Add file and stream in the logging already created before
logger.addHandler(file_handler)
file_handler.setLevel(logging.DEBUG)

# Handler to send messages to streams like sys.stdout, sys.stderr or any file-like object
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(console_formatter)
consolehandler.setLevel(logging.INFO)
logger.addHandler(consolehandler)

parser = argparse.ArgumentParser(description='Receive the arguments for the program')
parser.add_argument('-impn', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for NFC')
parser.add_argument('-impf', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for flow meter')
parser.add_argument('-impnotify', type=str, default='mock', choices=['mock', 'real'],
                    help='Choose between mock or real implementation for notification')
parser.add_argument('-f', type=str, default='template.cfg',
                    help='Configfile')


class nfckeg(object):
    """nfckeg"""

    def __init__(self, pin, impn, impf, impnotify, token, chat_id,logger):
        super(nfckeg, self).__init__()
        self.NFC = None
        self.Flow_meter = None
        self.notify = None
        self.Relay = None
        self.beer = {}
        self.pin = pin
        self.lastdata_FLOW = 0.0
        self.implementation_nfc = impn
        self.implementation_flow = impf
        self.implementation_notify = impnotify
        self.token = token
        self.chat_id = chat_id
        self.logger = logger

    # Function used to choose for each case the implementation for each instanced object
    def instance_objects(self):
        NFC_name = "NFC"
        Flow_name = "FLOW"

        if self.is_mock(self.implementation_nfc):
            self.NFC = sensors.mocksensor.NFCSensor(NFC_name)
        else:
            self.NFC = sensors.realsensor.NFCSensor(NFC_name)

        if self.is_mock(self.implementation_flow):
            self.Flow_meter = sensors.mocksensor.FlowSensor(Flow_name)
        else:
            self.Flow_meter = sensors.realsensor.FlowSensor(Flow_name, self.pin)
        if self.is_mock(self.implementation_notify):
            self.notify = notification.MockNotification(self.token, self.chat_id, self.logger)
        else:
            self.notify = notification.TelegramNotification(self.token, self.chat_id, self.logger)

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
        self.instance_objects()

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


# Function to check if there is a file with given name and create new template or read given file.
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


# Function that give information about wich field you have to fill
def read_cfg(file_name, config):
    config.read(file_name)
    write_config(config, file_name)
    remaining = get_remaining(config)
    if len(remaining) != 0:
        for section, option in remaining:
            logger.error('Fill option {} in section {}.Update file {}'.format(option, section, file_name))
        sys.exit()


# Check if in given configuration all values are filled, return a list with empty ones
def get_remaining(config):
    remaining = []
    for k, v in config._sections.items():
        for k1, v1 in v.items():
            if v1 == '':
                remaining.append((k, k1))
    return remaining


# Function that create a template to store configuration
def crear_plantilla():
    config = ConfigParser.RawConfigParser()
    config.add_section('Section1')
    config.set('Section1', 'pin', '')
    config.add_section('Notifications')
    config.set('Notifications', 'Token', '')
    config.set('Notifications', 'Chat_id', '')
    return config


# Function that write in a given file the given configuration
def write_config(config, file_name='template.cfg'):
    with open(file_name, 'wb') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    args = parser.parse_args()
    config = check_cfg(args.f)
    pin = get_value(config, 'Section1', 'pin')
    chat_id = get_value(config, 'Notifications', 'Chat_id')
    token = get_value(config, 'Notifications', 'Token')

    random.seed(2)
    NFCKEG = nfckeg(pin, args.impn, args.impf, args.impnotify, chat_id, token, logger)
    NFCKEG.main()
