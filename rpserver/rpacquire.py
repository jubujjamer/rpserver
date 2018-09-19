#!/usr/bin/python
# Red pitaya UCNP interface

import sys
from rpserver.redpitaya_scpi import scpi

import numpy as np
import time

class RpInstrument(object):
    def __init__(self, host):
        self.host =  host

    def acquire_channel(self, dec=1, channel=2):
        rp_s = scpi(self.host)
        rp_s.tx_txt('ACQ:DEC %i' % dec)
        rp_s.tx_txt('ACQ:TRIG:LEVEL 100')
        rp_s.tx_txt('ACQ:START')
        rp_s.tx_txt('ACQ:TRIG NOW')

        while 1:
            rp_s.tx_txt('ACQ:TRIG:STAT?')
            if rp_s.rx_txt() == 'TD':
                break

        rp_s.tx_txt('ACQ:SOUR%i:DATA?' % channel)
        buff_string = rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buff = list(map(float, buff_string))
        return np.array(buff)

    def acquire_decay(self, dec=1, channel=2):
        rp_s = scpi(self.host)
        rp_s.tx_txt('ACQ:DEC %i' % dec)
        rp_s.tx_txt('ACQ:TRIG:LEVEL 100')
        rp_s.tx_txt('ACQ:START')
        rp_s.tx_txt('ACQ:TRIG NOW')

        while 1:
            rp_s.tx_txt('ACQ:TRIG:STAT?')
            if rp_s.rx_txt() == 'TD':
                break

        rp_s.tx_txt('ACQ:SOUR%i:DATA?' % channel)
        buff_string = rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buff = list(map(float, buff_string))
        return np.array(buff)
