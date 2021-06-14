#!/usr/bin/env python
# coding: utf-8

import fire
import pandas as pd
import numpy as np
import sys
sys.path.insert(1, '/gpfs/fs2/scratch/awhite38_lab/cfdsr/alcfd/')
import utilities as utils

np.set_printoptions(precision=4, threshold=np.inf)

def run_cfd(name='cube1', d_start=0.005, d_end=0.1, t_start=1, t_end=180, v_start=0.02, v_end=0.005, dim=10):

    print(f'Running with {name}')
    dim = dim
    D = np.linspace(d_start, d_end, dim, endpoint=False)
    theta = np.linspace(t_start, t_end, dim, dtype=int, endpoint=False)
    v = np.linspace(v_start, v_end, dim)
    
    dd, tt, vv = np.meshgrid(D, theta, v, indexing='ij')
    grid_3d = np.array([(i, j, k) for i,j,k in zip(dd.flatten(), tt.flatten(), vv.flatten())])
    samples = grid_3d.shape[0]
    
    inlet_p = np.array([101325 for _ in range(samples)]) # [Pa]
    rho = np.array([998 for _ in range(samples)]) # [kg m^-3]
    muo = np.array([9.737e-4 for _ in range(samples)]) # [Pa s]
    
    inputs_3d_grid = [grid_3d[:,0], grid_3d[:,1], grid_3d[:,2], rho, muo, inlet_p]
    
    re_number = utils.check_laminar(grid_3d[:,0], rho, grid_3d[:,2], muo)
    #print(re_number)
    
    outputs_3d_grid = utils.run_model(pipe_D=grid_3d[:, 0], 
                                      bend_angle=grid_3d[:, 1], 
                                      inlet_v=grid_3d[:, 2], 
                                      rho=rho, 
                                      muo=muo, 
                                      inlet_p=inlet_p, 
                                      name=name, 
                                      run_parallel=True)

def main():
    fire.Fire(run_cfd)

if __name__ == '__main__':
    main()
