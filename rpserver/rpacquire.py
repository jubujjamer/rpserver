import sys
import warnings

from rpserver.redpitaya_scpi import scpi

import numpy as np
import time

class Options(object):
    def __init__(self, nsamples=1E6, timeout=1E3, maxwindows=1E5):
       self.nsamples = int(nsamples)
       self.timeout = int(timeout)
       self.maxwindows = int(maxwindows)

class RpInstrument(object):
    def __init__(self, host, decimation, channel, trigger_channel, opts, size=8000, sim=False):
            self.size = int(size) # Read buffer data size
            self.opts = opts
            self.host = host
            self.ts = float(decimation)/125E6 # Sampling time
            self.simflag = sim
            self.buflen = 16364
            self.trigger_level = 0
            self.trigger_start = 0
            self.trigger_stop = self.buflen - 1
            self.trigger_period = 0
            self.calibrated_flag = False
            if channel is 1:
                self.trigger_channel = 2
            elif channel is 2:
                self.trigger_channel = 1
            self.channel = channel
            if self.trigger_channel != trigger_channel:
                warning.warn('Selected trigger channel was not correct.')

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
                self.rp_s.tx_txt('ACQ:SOUR2:GAIN HV')
                print('Red Pitaya parameters set OK.')
            else:
                print('Runing a simulated version of the driver')

    def acquire_channel(self):
        # Clean the buffer
        self.rp_s.tx_txt('ACQ:SOUR%i:DATA?' % self.channel)
        self.rp_s.rx_txt()
        self.rp_s.tx_txt('ACQ:TRIG NOW')
        self.rp_s.tx_txt('ACQ:START')
        while 1:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            if self.rp_s.rx_txt() == 'TD':
                    break
        self.rp_s.tx_txt('ACQ:SOUR%i:DATA?' % self.channel)
        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buff = list(map(float, buff_string))
        time_array = np.linspace(0, len(buff)*self.ts, len(buff))
        return time_array, np.array(buff)


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
            self.rp_s.tx_txt('ACQ:TRIG:LEVEL %.1f' % self.trigger_level)
            self.rp_s.tx_txt('ACQ:TRIG CH%i_NE' % self.trigger_channel)
            self.rp_s.tx_txt('ACQ:START')
            while 1:
                self.rp_s.tx_txt('ACQ:TRIG:STAT?')
                if self.rp_s.rx_txt() == 'TD':
                    break

            self.rp_s.tx_txt('ACQ:SOUR%i:DATA?' % self.channel)
            buff_string = self.rp_s.rx_txt()

            buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
            signal = np.array(list(map(float, buff_string)))
        else:
            signal = self.generate_simulated_signal()

        time_array = np.linspace(0, len(signal)*self.ts, len(signal))
        return time_array, signal

    def calibration_run(self):
        """ Calibrates the level and edges of the trigger signal.
        """
        status_message = ''
        if not self.simflag:
            self.rp_s.tx_txt('ACQ:START')
            self.rp_s.tx_txt('ACQ:TRIG CH%i_NE' % self.trigger_channel)
            self.rp_s.tx_txt('ACQ:TRIG:DLY %i' % (self.buflen//2))
            while 1:
                self.rp_s.tx_txt('ACQ:TRIG:STAT?')
                if self.rp_s.rx_txt() == 'TD':
                        break
            self.rp_s.tx_txt('ACQ:SOUR%i:DATA?' % self.trigger_channel)
            buff_string = self.rp_s.rx_txt()
            buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
            signal = np.array(list(map(float, buff_string)))
        else:
            signal = self.generate_simulated_trigger()
        time_array = np.linspace(0, len(signal)*self.ts, len(signal))
        # Acquisition endend. Finding trigger level and indexes.
        diff_trigger = np.diff(signal)
        # Find the center of the signal to use it as trigger level
        trigger_level = (signal.max() + signal.min())/2
        self.trigger_level = trigger_level
        # Find start and end of trigger pulse
        start_index = np.where(signal<trigger_level)[0][0]
        try:
            stop_index = np.where(signal[self.buflen//2:]>trigger_level)[0][1]+self.buflen//2
        except:
            stop_index = -1
        if (stop_index - start_index) < self.buflen//2:
            status_message = "Trigger signal too short, decrease frequency."
        elif stop_index == self.buflen:
            status_message += "Warning: signal trigger may be too slow."
        trigger_duration = stop_index - start_index
        signal_period = trigger_duration*self.ts
        self.trigger_stop = stop_index
        self.trigger_start = start_index
        self.trigger_period = signal_period
        self.calibrated_flag = True
        # Calibration OK message
        status_message += "Calibration OK. Trigger frequency is: %.3f" % (0.5/signal_period)
        return time_array, signal, status_message

    def acquire_decay(self):
        """ Measures decay with a photon counting approach.
        """
        status_message = ''
        if not self.calibrated_flag:
            status_message = "Warning: No previous calibration. Perfoming calibration..."
            print(status_message)
            self.calibration_run()
        counts = np.array([])
        start = time.time()
        lapse = 0
        status_message = 'Initiating measurement.'
        for k in range(self.opts.maxwindows):
            time_now = time.time()-start
            t, signal = self.acquire_triggered()
            # Find singal edges
            signal_triggered = signal[self.trigger_start: self.trigger_stop]
            sig_diff = np.diff(signal_triggered, n=1)
            diff_level = (sig_diff.max())/6
            edge_positions = np.where(sig_diff > diff_level)[0]
            counts = np.hstack((counts , edge_positions))
            times = counts*self.ts
            hist, bins = np.histogram(times, bins=160)
            if time_now-lapse > 1:
                status_message = 'Remaining time %.3f s' % (time_now*(self.opts.nsamples-len(counts))/len(counts))
                print(status_message)
                lapse = time_now
            # Ending conditions
            if time_now-start > self.opts.timeout:
                status_message = 'Timeout reached.'
                print(status_message)
                yield hist, bins, status_message
                return
            if len(counts)>self.opts.nsamples:
                status_message = 'Measurement ready. Collected %i samples in %.1f s.' % (len(counts), time_now)
                print(status_message)
                yield hist, bins, status_message
                return
            yield hist, bins, status_message
