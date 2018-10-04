import numpy as np
import h5py
import matplotlib.pylab as plt
# Open an example filename for visualization

fin = h5py.File("557-20181003-180449.hdf", "r")
plt.plot(fin['time'], fin['idata'])
for key, val in fin['idata'].attrs.items():
    print(key, val)
plt.show()
