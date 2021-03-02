import subprocess
import pandas as pd
import os
import sys
import numpy as np


def run_model(pipe_D, bend_angle, rho, muo, inlet_v, inlet_p):
        input_dict = {'D': pipe_D, 'Angle': bend_angle, 'Density': rho,
                'Viscosity': muo, 'V_in': inlet_v, 'P_in': inlet_p}
        df = pd.DataFrame(input_dict)
        df.to_csv('inputs.txt', header=True, sep='\t', index=None)
        check_laminar(pipe_D, rho, inlet_v, muo)
        script = 'archived_models/elbowed_pipe/script.wbjn'
        wb = '/scratch/dfoster_lab/ansys2020R2/v202/Framework/bin/Linux64/runwb2'
        cmdline = '{} -B -R {}'.format(wb, script)
        try:
                os.system(cmdline)
        except Exception:
                print('Failed to launch ANSYS Workbench!')
                sys.exit(0)
        outputs = pd.read_csv('outputs.txt', delimiter='\t')
        print('Results are stored in outputs.txt')
        return outputs


def check_laminar(pipe_D, rho, inlet_v, muo):
    re_number = rho*inlet_v*pipe_D/muo
    a = np.where(re_number > 2100)[0]
    assert len(
        a) == 0, f'Model input {a} parameters will result a turbulent flow. Revise parameters!'
    return re_number

def compute_Hagen_Poiseuille_del_P(muo, l, inlet_v, pipe_D):
    del_p = 32 * muo * l * inlet_v / pipe_D**2
    return del_p


# def execute_subprocess(cmd):
#     from __future__ import print_function  # Only Python 2.x
#     popen = subprocess.Popen(
#         cmd, stdout=subprocess.PIPE, universal_newlines=True)
#     for stdout_line in iter(popen.stdout.readline, ""):
#         yield stdout_line
#     popen.stdout.close()
#     return_code = popen.wait()
#     if return_code:
#         raise subprocess.CalledProcessError(return_code, cmd)


# def run_model_debug():
#         cmdline = '/scratch/dfoster_lab/ansys2020R2/v202/Framework/bin/Linux64/runwb2 -B -R archived_models/elbowed_pipe/script.wbjn'
#         # for debugging uncomment
#         for path in execute_subprocess(cmdline.split(' ')):
#                 print(path, end="")
