#!/usr/bin/env python
# -*-coding:utf_8-*-
import argparse
import logging
import random
import sys
import time
from collections import defaultdict

import ConfigParser

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
parser.add_argument('-u', type=str, default='broadcast',
                    help='Choose to notify by broadcast to all users from configfile or the specific user')


class nfckeg(object):
    def __init__(self, pin, impn, impf, impnotify, token, chat_id, user, logger):
        super(nfckeg, self).__init__()
        self.NFC = None
        self.Flow_meter = None
        self.notify = None
        self.Relay = None
        self.beer = defaultdict(int)
        self.pin = pin
        self.lastdata_FLOW = 0.0
        self.implementation_nfc = impn
        self.implementation_flow = impf
        self.implementation_notify = impnotify
        self.token = token
        self.chat_id = chat_id
        self.logger = logger
        self.user = user

    # Function used to choose for each case the implementation for each instanced object
    def instance_objects(self):
        NFC_name = "NFC"
        Flow_name = "FLOW"
        ESPFlow_name = "GUEST"

        if is_mock(self.implementation_nfc):
            self.NFC = sensors.mocksensor.NFCSensor(NFC_name)
        else:
            self.NFC = sensors.realsensor.NFCSensor(NFC_name)

        if is_mock(self.implementation_flow):
            self.Flow_meter = sensors.mocksensor.FlowSensor(Flow_name)
        else:
            self.Flow_meter = sensors.realsensor.FlowSensor(Flow_name, self.pin)
        self.Flow_meter.setup()
        self.ESPFlow_meter = sensors.realsensor.ESPFlow(ESPFlow_name, logger)
        self.ESPFlow_meter.setup()
        if is_mock(self.implementation_notify):
            self.notification = notification.MockNotification(self.token, self.chat_id, self.logger)
        else:
            self.notification = notification.TelegramNotification(self.token, self.chat_id, self.logger)

    # Function used to get NFC identification and we assign a flow value.
    def get_state(self):
        self.NFC.setup()
        data_NFC = self.NFC.get_data()
        self.ESP_data()
        # In case that there are any NFC value, relay will turn on.
        if data_NFC is not None:
            logger.info('NFC {} detected'.format(data_NFC))
            logger.info('Relay on with music')

            while True:
                self.Flow_meter.update()
                data_FLOW = self.Flow_meter.get_data()

                # If there is a flow, assign the quantity of beer to its NFC card.
                if data_FLOW != 0:
                    self.Flow_meter.reset_data()
                    self.beer[data_NFC] += data_FLOW
                    # If it's not the first value, calculate the difference between last value and the current one.
                    logger.info('Difference: {}'.format(data_FLOW))
                    break
            logger.info('Relay off')
            self.send_updated_info()

    def send_updated_info(self):
        logger.info("This is the cumulative of beer: {} Litro(s)".format(self.Flow_meter.get_cumulative()))

        for tarjetas in self.beer:
            message = ('{}: {}'.format(tarjetas, self.beer[tarjetas]))
            self.notifier(message)

    def ESP_data(self):
        data_ESP = self.ESPFlow_meter.get_data()
        for value in data_ESP:
            self.beer['guest'] += value
        if data_ESP:
            self.notifier('guest: {} ({} beer/s)'.format(self.beer['guest'], len(data_ESP)))

    def notifier(self, message):
        if self.user == 'broadcast':
            self.notification.broadcast(message)
        else:
            self.notification.notify(self.user, message)

    # In the main loop we create the instances and get the value every n seconds.
    def main(self):
        self.instance_objects()
        try:
            while True:
                self.get_state()
                time.sleep(1)
        except:
            self.ESP_data()
            for tarjetas in self.beer:
                logger.info("For NFC {}: {} Litro(s)".format(tarjetas, self.beer[tarjetas]))


# Function to check if there is a file with given name and create new template or read given file.
def check_cfg(file_name):
    import os.path
    config = crear_plantilla()
    if os.path.isfile(file_name):
        read_cfg(file_name, config)
    else:
        write_config(config)
        logger.error('Config file {} not found. Update the new template: '.format(file_name))
        logger.info('-"pin" is the pin of flow sensor\n\
         -"Token" is the token of the bot telegram\n\
         -"Chat_id" is the chat_id of the bot telegram.\n\
         ***If It is a list of users use a " "(space) to separate them***')
        sys.exit()
    return config


def get_value(config, section, option):
    return config.get(section, option)


# Function that give information about which field you have to fill
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
    return [(k, k1) for k, v in config._sections.items() for k1, v1 in v.items() if v1 == '']


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


def is_mock(item):
    return item == 'mock'


def is_esp(item):
    return item == 'esp'


if __name__ == '__main__':
    args = parser.parse_args()
    config = check_cfg(args.f)
    pin = int(get_value(config, 'Section1', 'pin'))
    chat_id = get_value(config, 'Notifications', 'Chat_id')
    token = get_value(config, 'Notifications', 'Token')

    random.seed(2)
    NFCKEG = nfckeg(pin, args.impn, args.impf, args.impnotify, token, chat_id, args.u, logger)
    NFCKEG.main()
