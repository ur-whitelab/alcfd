#!/bin/bash
#SBATCH -p awhite
#SBATCH --time 00:30:00

#SBATCH -N 1
#SBATCH --mem=64gb 
#SBATCH --cpus-per-task=1
####################################################
##########MACHINE SPECIFIC DETAILS GO HERE##########
####################################################

module load anaconda/2019.10
source activate alcfd
cd /gpfs/fs2/scratch/awhite38_lab/cfdsr/alcfd/examples

python pipe_flow_parallel.py $m
# rm -rf slurm*