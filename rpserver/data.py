# -*- coding: utf-8 -*-
"""
file data.py
author: Juan Marco Bujjamer

Data fitting for UCNP curves.
"""
import os
import numpy as np
import collections
import matplotlib.pylab as plt
import scipy
import pandas as pd
from . import fitting as df
import yaml

DATA_FOLDER = '/home/lec/pCloudDrive/doctorado/UCNP/meds/'
SPEC_DEFAULT = 'specs.txt'
SPEC_YAML = 'data_info.yaml'
DATA_DEFAULT = 'data.yaml'

def UCNPEmission(object):
    def __init__(self):
        __all__ = ['__init__']

def load_idecay(daystr, filename, nbins=60, ndata=-1, TS=6.4E-8):
    basedir = os.path.join(DATA_FOLDER, daystr)

    data_fin = os.path.join(basedir, filename + '.npy')
    text_fin = os.path.join(basedir, filename + '.txt')
    # with open(text_fin, 'r') as textfile:
    #     title = textfile.readlines()[3]
    title = filename
    time_data = np.load(data_fin)*TS
    hist, edges = np.histogram(time_data, bins=nbins, density=False)
    times = edges[0:-1]
    y = hist - np.mean(hist[-nbins//20: -1])
    ydata = y/np.max(y)
    return times, ydata

def load_mean_times(daystr, filename, nbins=60, ndata=-1, TS=6.4E-8):
    basedir = os.path.join(DATA_FOLDER, daystr)

    data_fin = os.path.join(basedir, filename + '.npy')
    text_fin = os.path.join(basedir, filename + '.txt')
    title = filename
    time_data = np.load(data_fin)*TS
    return np.mean(time_data)


def get_timesets(daystr, nbins=2500, model='mixture', filtering=True,
                 ndata=-1, datafile=DATA_DEFAULT):
    """ Load time decay data.

    Parameters
    ----------
    daystr : string
        Name of the stored data folder (e.g. 2017-09-22).
    nbins : int
        Number of bins points used in the time data.
    model : string
        Model for the data fitting. Supported models in fitting.fit_exponential().
    filtering : bool
        Should the data be previously filtered or not.
    ndata : int
        Number of points in each time series.
    datafile : string
        yaml file with extra information on the measurements.

    Returns
    -------
    list
        Description of returned object.

    """
    import yaml
    basedir = os.path.join(DATA_FOLDER, daystr)
    yaml_fin = os.path.join(basedir, datafile)
    with open(yaml_fin, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
            datasets = yaml_data['datasets']
        except yaml.YAMLError as exc:
            print(exc)

    datasets_list = list()
    for key, filenames in iter(datasets.items()):
        datasets_list.append(get_time_data(daystr, nbins=nbins, model=model,
                                           filtering=filtering, ndata=ndata,
                                           filenames=filenames, datafile=datafile))
    return datasets_list



def load_timedata(daystr, filenames, nbins=60, ndata=-1):

    TS = 6.4E-8 # TODO: get this from the config file
    basedir = os.path.join(DATA_FOLDER, daystr)
    data_list = list()
    for filename in filenames:
        data_fin = os.path.join(basedir, filename + '.npy')
        text_fin = os.path.join(basedir, filename + '.txt')
        textfile = open(text_fin, 'r')
        title = textfile.readlines()[3]
        title = filename
        textfile.close()
        time_data = np.load(data_fin)*TS
        NACQ = len(time_data)
        hist, edges = np.histogram(time_data, bins=nbins, density=False)
        times = edges[0:-1]
        y = hist - np.mean(hist[-nbins//20: -1])
        ydata = y/np.max(y)
        data_list.append((times[:ndata], ydata[:ndata], title))
    return data_list


def get_time_data(daystr, nbins=2500, model='mixture', filtering=True, ndata=-1,
                  filenames=None, datafile=DATA_DEFAULT):
    import yaml
    basedir = os.path.join(DATA_FOLDER, daystr)
    yaml_fin = os.path.join(basedir, datafile)
    with open(yaml_fin, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    b, a = scipy.signal.butter(2, 0.3)# Para el filtrado (de ser necesario)
    data_list = list()
    # Hago los ajustes y guardo los parámetros ajustados
    for tdata, ydata, title in load_timedata(daystr, filenames,
                                             nbins=nbins, ndata=ndata):
        if filtering:
            ydata = scipy.signal.filtfilt(b, a, ydata)
        result = df.robust_fit(tdata, ydata, model=model)
        data_list.append((tdata, ydata, result))
    return data_list



def print_datainfo(daystr, filenames):
    basedir = os.path.join(DATA_FOLDER, daystr)
    data_list = list()
    for filename in filenames:
        data_fin = os.path.join(basedir, filename + '.npy')
        text_fin = os.path.join(basedir, filename + '.txt')
        textfile = open(text_fin, 'r')
        datainfo = textfile.readlines()
        textfile.close()
        print(filename)
        print(datainfo)
    return


def load_spectrum(daystr, meas_n, fname=None):
    """ Get Felix PTI spectrum.wavelength_list
    """
    basedir = os.path.join(DATA_FOLDER, daystr)
    if not fname:
        # data_fin = os.path.join(basedir, SPEC_DEFAULT)
        fname = SPEC_DEFAULT
    data_fin = os.path.join(basedir, fname)

    columns = list()
    for i in range(132):
        columns.append(str(i))
    table = pd.read_csv(data_fin, header=None, delimiter='\t', names=columns)
    head = 4
    x = table[str((meas_n-1)*2)][head:]
    y = table[str((meas_n-1)*2+1)][head:]
    x = np.array([float(x_i) for x_i in x])
    y = np.array([float(y_i) for y_i in y])
    try:
        first_nan = np.where(np.isnan(x))[0][0]
    except:
        first_nan = -1
    return x[:first_nan], y[:first_nan]

def load_multiple_spectra(daystr, datafile=DATA_DEFAULT):
    import yaml
    basedir = os.path.join(DATA_FOLDER, daystr)
    yaml_fin = os.path.join(basedir, datafile)
    spec_collection = []
    with open(yaml_fin, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
            spectrum_names = yaml_data['spectrum_names']
            spectra_to_plot = yaml_data['spectra_to_plot']
        except yaml.YAMLError as exc:
            print(exc)
    for m in spectra_to_plot:
        x, y = load_spectrum(daystr, m)
        y = y - np.mean(y[-10:-1])
        spec_collection.append( (np.asarray(x), np.asarray(y)) )
        # if m == 2:
        #     norm = scipy.integrate.simps(y)
        # pvals.append(scipy.integrate.simps(y)/norm)
    return spec_collection



def get_powers(daystr, datafile=None):
    basedir = os.path.join(DATA_FOLDER, daystr)
    yaml_fin = os.path.join(basedir, datafile)
    with open(yaml_fin, 'r') as stream:
        try:
            yaml_data = yaml.load(stream)
            lpowers = yaml_data['laser_vpp_list']
        except yaml.YAMLError as exc:
            print(exc)
    return lpowers


def integrate_power(x, y, center=540, bwidth=10):
    ci = np.where(x==center)[0][0]  # Center index
    intp = scipy.integrate.simps(y[ci-bwidth//2:ci+bwidth//2])
    return intp


def get_timepars(daystr=None, nbins=1200, model='double_neg', filtering=False,
                 ndata=300, dsnumber=0, datafile=DATA_DEFAULT):
    datasets_list = get_timesets(daystr, nbins=nbins, model=model,
                                 filtering=filtering, ndata=ndata,
                                 datafile=datafile)
    dataset = datasets_list[dsnumber]
    a1_list, a2_list, ka_list, kUC_list = list(), list(), list(), list()
    for tdata, ydata, results in dataset:
        a1_list.append(results.params['a1'].value)
        a2_list.append(results.params['a2'].value)
        ka_list.append(results.params['ka'].value)
        kUC_list.append(results.params['kUC'].value)
    return np.array(a1_list), np.array(a2_list), np.array(ka_list), np.array(kUC_list)


def load_data(daystr, config_file=None):
    basedir = os.path.join(DATA_FOLDER, daystr)
    if config_file is not None:
        yaml_fin = config_file
    else:
        yaml_fin = os.path.join(basedir, DATA_DEFAULT)
    print(yaml_fin)
    config_dict = yaml.load(open(yaml_fin, 'r'))
    config = collections.namedtuple('config', config_dict.keys())
    cfg = config(*config_dict.values())
    return cfg
