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

DATA_FOLDER = 'etc'
DATA_DEFAULT = 'etc'
def load_data(data_file=None):
    config_file = os.path.join(DATA_FOLDER, data_file)
    config_dict = yaml.load(open(config_file, 'r'))
    config = collections.namedtuple('config', config_dict.keys())
    cfg = config(*config_dict.values())
    return cfg
