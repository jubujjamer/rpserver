import sys
from rpserver.redpitaya_scpi import scpi

import numpy as np
import time

class RpInstrument(object):
    def __init__(self, host, decimation, channel, trigger, size=8000):
            self.size = int(size) # Read buffer data size
            self.host = host
            self.channel = int(channel)
            self.trigger = trigger
            self.ts = float(decimation)/125E6 # Sampling time
            try:
                self.rp_s = scpi(self.host)
                self.rp_s.tx_txt('ACQ:DEC %i' % decimation)
            except:
                raise Exception("Check Red Pitaya is connected.")
            try:
                self.rp_s.tx_txt('ACQ:TRIG:LEVEL %i' % 100)
            except:
                raise Exception("Could'nt set trigger level.")
            # No I change gains manually
            self.rp_s.tx_txt('ACQ:SOUR1:GAIN HV')
            self.rp_s.tx_txt('ACQ:SOUR2:GAIN HV')
            print('RP parameters set OK')

    def acquire_channel(self):
        print(self.rp_s.tx_txt('ACQ:BUF:SIZE?'))
        self.rp_s.tx_txt('ACQ:START')
        # Clean the buffer
        self.rp_s.tx_txt('ACQ:SOUR1:DATA?')
        try:
            self.rp_s.tx_txt('ACQ:TRIG %s' % self.trigger)
        except:
            raise Exception("Could'nt set trigger to %s." % self.trigger)
        while 1:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            if self.rp_s.rx_txt() == 'TD':
                    break
        # self.rp_s.tx_txt('ACQ:SOUR1:DATA?')
        self.rp_s.tx_txt('ACQ:SOUR1:DATA?')

        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buff = list(map(float, buff_string))
        time = np.linspace(0, len(buff)*self.ts, len(buff))
        return time, np.array(buff)

    def calibration_run(self):
        """ Measures decay with a photon counting approach.
        """
        self.rp_s.tx_txt('ACQ:START')
        try:
            self.rp_s.tx_txt('ACQ:TRIG %s' % self.trigger)
        except:
            raise Exception("Could'nt set trigger to %s." % self.trigger)
        while 1:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            if self.rp_s.rx_txt() == 'TD':
                    break
        self.rp_s.tx_txt('ACQ:SOUR1:DATA?')
        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        signal = np.array(list(map(float, buff_string)))
        time = np.linspace(0, len(signal)*self.ts, len(signal))
        # Find the center of the signal to use it as trigger level
        trigger_level = (signal.max() + signal.min())/2
        self.rp_s.tx_txt('ACQ:TRIG:LEVEL %.1f' % trigger_level)
        self.rp_s.tx_txt('ACQ:TRIG CH2_NE')
        print(trigger_level)
        return time, np.array(signal)
