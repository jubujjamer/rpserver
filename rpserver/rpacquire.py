import sys

from rpserver.redpitaya_scpi import scpi

import numpy as np
import time

class RpInstrument(object):
    def __init__(self, host, decimation, channel, trigger, size=8000, sim=False):
            self.size = int(size) # Read buffer data size
            self.host = host
            self.channel = int(channel)
            self.trigger = trigger
            self.ts = float(decimation)/125E6 # Sampling time
            self.simflag = sim
            self.buflen = 16364
            self.trigger_level = 0
            self.trigger_start = 0
            self.trigger_stop = self.buflen - 1 
            self.trigger_period = 0
            if not sim:
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
            else:
                print('Runing a simulated version of the driver')

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

    
    def generate_simulated_trigger(self):
         noise = 0.1*np.random.randn(self.buflen)

         siglen = np.random.randint(11000, 13000)
         init = np.random.randint(0, 1000)
         square = np.zeros(self.buflen)
         square[init:init+siglen] = 1
         square = square + noise - 0.4
          
         return square

    def generate_simulated_signal(self):
         noise = 0.1*np.random.randn(self.buflen)
         npulses = np.random.randint(5, 25)
         indexes = range(self.buflen)
         start_indexes = np.random.sample(npulses)*self.buflen
         pulses = np.zeros(self.buflen)
         for i in start_indexes:
            i = int(i)
            d = np.random.randint(10, 100)
            pulses[i:i+d] = -1
         pulses = pulses + noise + 0.8
         return pulses
          
    def acquire_triggered(self):
        """ Measures decay with a photon counting approach.
        """
        if not self.simflag:
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
        else:
            signal = self.generate_simulated_signal()
        time = np.linspace(0, len(signal)*self.ts, len(signal))
        return time, signal

    def calibration_run(self):
        """ Measures decay with a photon counting approach.
        """
        if not self.simflag:
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
        else:
            signal = self.generate_simulated_trigger()
        time = np.linspace(0, len(signal)*self.ts, len(signal))
        diff_trigger = np.diff(signal)
        # Find the center of the signal to use it as trigger level
        trigger_level = (signal.max() + signal.min())/2
        self.trigger_level = trigger_level
        # Find start and end of trigger pulse
        start_index = np.where(signal>trigger_level)[0][0]
        stop_index = np.where(signal>trigger_level)[0][-1]
        if (stop_index - start_index) < self.buflen//2:
            raise Exception("Signal too short, increase frequency.")
        elif stop_index == self.buflen:
            print("Warning: signal trigger too slow.")
        trigger_duration = stop_index - start_index
        signal_period = trigger_duration*self.ts
        self.trigger_stop = stop_index
        self.trigger_start = start_index
        self.trigger_period = signal_period
        return time, np.array(signal)
    
    def acquire_decay(self):
        """ Measures decay with a photon counting approach.
        """
        if not self.simflag:
            self.rp_s.tx_txt('ACQ:START')
            try:
                self.rp_s.tx_txt('ACQ:TRIG %s' % self.trigger)
            except:
                raise Exception("Couldn't set trigger to %s." % self.trigger)
            while 1:
                self.rp_s.tx_txt('ACQ:TRIG:STAT?')
                if self.rp_s.rx_txt() == 'TD':
                        break
            self.rp_s.tx_txt('ACQ:SOUR1:DATA?')
            buff_string = self.rp_s.rx_txt()
            buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
            signal = np.array(list(map(float, buff_string)))
        else:
            signal = self.generate_simulated_signal()
        time = np.linspace(0, len(signal)*self.ts, len(signal))
        # Find singal edges
        signal_triggered = signal[self.trigger_start: self.trigger_stop] 
        sig_diff = np.diff(signal_triggered, n=1)
        diff_level = (diff_level.max()-diff_level.min())/2
        edge_positions = np.where(sig_diff < diff_level)[0]
        
        return time, signal
