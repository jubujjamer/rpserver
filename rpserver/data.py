# -*- coding: utf-8 -*-
"""
file data.py
author: Juan Marco Bujjamer

Data fitting for UCNP curves.
"""
import os
import numpy as np
import collections
import scipy
import pandas as pd
import yaml
import h5py

DATA_FOLDER = 'etc'
DATA_DEFAULT = 'etc'

def load_data(data_file=None):
    config_file = os.path.join(DATA_FOLDER, data_file)
    config_dict = yaml.load(open(config_file, 'r'))
    config = collections.namedtuple('config', config_dict.keys())
    cfg = config(*config_dict.values())
    return cfg

def save_h5f_data(filename, counts, time, idata, wavelength, laser_power, frequency, duty_cycle,
                  optical_filter):
    with h5py.File(filename, "w") as f:
        f.create_dataset("time", data=time)
        cdset = f.create_dataset("counts", data=counts)
        idset = f.create_dataset("idata", data=idata)
        idset.attrs['wavelength'] = wavelength
        idset.attrs['laser_power'] = laser_power
        idset.attrs['duty_cycle'] = duty_cycle
        idset.attrs['optical_filter'] = optical_filter
