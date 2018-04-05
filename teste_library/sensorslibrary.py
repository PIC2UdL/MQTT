#!/usr/bin/env python
#-*-coding:utf_8-*-

import random
import time

class Sensorslibrary(object):
    """Sensorlibrary"""
    def __init__(self):
        super(Sensorlibrary, self).__init__()

    @staticmethod
    def nfc():
        time.sleep(5)
        if random.randint(1,100) == 98:
            return random.choice(['ABCD136468', 'BCDE789514', 'CDEF663247'])
        return None

    @staticmethod
    def flow():
        flow = None
        time.sleep(3)
        if random.randint(1,100) == 98:
            a = 50
            while a > 0:
                flow = random.random(0.0,1.0)
                a -= 1
                time.sleep(1)
        return flow
