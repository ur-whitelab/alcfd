import subprocess
import pandas as pd
import os
import sys
import numpy as np
import shutil


def run_model(pipe_D, bend_angle, inlet_v, rho=1.225, muo=1.7894e-5, inlet_p=101325, l_d_ratio=None, name=None, debug=False, run_parallel=False):
    if l_d_ratio is None:
        l_d_ratio = 10
        print(f'No input was given for pipe L/D. Assuming L/D = {l_d_ratio}.')
    if name is None:
        name = ''
    path = os.getcwd()
    inputs_dir = path + '/inputs' + f'_{name}.txt'
    outputs_dir = path + '/outputs' + f'_{name}.txt'
    input_types = (list, int, float, np.float64, np.int)
    inputs = [pipe_D, bend_angle, inlet_v, rho, muo, inlet_p]
    for i, input in enumerate(inputs):
        if isinstance(input, input_types):
            inputs[i] = np.array(input)[np.newaxis,...]
    pipe_D, bend_angle, inlet_v, rho, muo, inlet_p = inputs
    input_dict = {'D': pipe_D, 'L_D_ratio': l_d_ratio, 'Angle': bend_angle, 'Density': rho,
                  'Viscosity': muo, 'V_in': inlet_v, 'P_in': inlet_p, 'outputs_file': outputs_dir}
    df = pd.DataFrame(input_dict)
    re_number, index_turbulent = check_laminar(pipe_D, inlet_v, rho, muo)
    if index_turbulent.size != 0:
        for i in index_turbulent:
            df = df.drop(index=i)
        print(
            f'Warning: Dropped inputs {index_turbulent} as they result a turbulent flow.')
    if not df.empty:
        print('Inputs to the model are:\n{}'.format(df))
        df.to_csv(inputs_dir, header=True, sep='\t', index=None)
        print(f'Model inputs are saved in:\n {inputs_dir}') 
        # re_number, a = check_laminar(pipe_D, rho, inlet_v, muo)
        wb = '/scratch/dfoster_lab/ansys2020R2/v202/Framework/bin/Linux64/runwb2'
        script = '/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/script.wbjn'
        if not run_parallel:
            shutil.copyfile(
                inputs_dir, '/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/inputs.txt')
        else:
            ProjectPath = f'/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/elbowed_pipe_{name}.wbpj'
            input_file = inputs_dir
            with open(script, "r") as f:
                lines = f.readlines()
                for m, line in enumerate(lines):
                    if line.startswith('input_file'):
                        lines[m] = f'input_file = "{input_file}"\n'
                    if line.startswith('    ProjectPath'):
                        lines[m] = f'    ProjectPath="{ProjectPath}",\n'
            script_parallel = f'/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/script_parallel_{name}.wbjn'
            with open(script_parallel, "w") as f:
                lines = "".join(lines)
                f.write(lines)
            script = script_parallel
        if debug:
            cmdline = f'{wb} -B -R {script} > run_log_{name}.txt'
        else:
            cmdline = f'{wb} -B -R {script}'
        try:
                os.system(cmdline)
        except Exception:
                print('Failed to launch ANSYS Workbench!')
                sys.exit(0)
        outputs = pd.read_csv(outputs_dir, delimiter='\t')
        outputs = outputs.drop(columns=['Mesh max size', 'Pipe R', 'Pipe L', 'p0', 'p1'])
        print(f'Results are stored in:\n {outputs_dir}.')
        if run_parallel:
            shutil.rmtree(
                f'/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/elbowed_pipe_{name}_files')
            os.remove(
                f'/scratch/awhite38_lab/cfdsr/alcfd/archived_models/elbowed_pipe/elbowed_pipe_{name}.wbpj')
            os.remove(script)
        return outputs
    else: 
        print('Model cannot run. All inputs resulted a turbulent flow.')


def check_laminar(pipe_D, inlet_v, rho, muo):
    re_number = rho*inlet_v*pipe_D/muo
    input_types = (list, int, float, np.float64, np.int)
    if isinstance(re_number, input_types):
        re_number = np.array(re_number)[np.newaxis, ...]
    index_turbulent = np.where(re_number > 2100)[0]
    if index_turbulent.size != 0:
        print(
            f'Model input {index_turbulent} parameters will result a turbulent flow. Revise parameters!\nUnacceptable Re = {re_number[index_turbulent]}')
    return re_number, index_turbulent

def compute_Hagen_Poiseuille_del_PL(muo, inlet_v, pipe_D):
    del_pl = 32 * muo  * inlet_v / pipe_D**2
    return del_pl


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
