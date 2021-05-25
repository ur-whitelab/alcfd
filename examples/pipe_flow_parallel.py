import sys
sys.path.insert(1, '/gpfs/fs2/scratch/awhite38_lab/cfdsr/alcfd')
import utilities as utils
import os
import pandas as pd
import numpy as np


pipe_D = np.array([0.01, 0.025, 0.05, 0.1, 0.2]) # [m]
bend_angle = np.array([1, 30, 60, 90, 120]) # [degrees]
rho = np.array([1.225]*5) # [kg m^-3]\n",
muo = np.array([1.7894e-5]*5) # [Pa s]
inlet_v = np.array([0.1]*5) # [m/s]\n",
inlet_p = np.array([101325]*5) # [Pa]

k = int(sys.argv[1])
inputs = [pipe_D[k], bend_angle[k], inlet_v[k], rho[k], muo[k], inlet_p[k]]
outputs = utils.run_model(*inputs, name=f'parallel_{k}', debug=True, run_parallel=True)
