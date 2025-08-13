#!/bin/bash
#SBATCH -p orfoz
#SBATCH -A skankinou
#SBATCH -J orfoztest
#SBATCH -N 1
#SBATCH --ntasks=110                # Total 8 MPI ranks (2 per node)
##SBATCH --ntasks-per-socket=110
#SBATCH --mem=140GB
#SBATCH --time=3-00:00:00
#SBATCH -C weka
#SBATCH --error=slurm-%j.err


bash run1_gau.sh 
