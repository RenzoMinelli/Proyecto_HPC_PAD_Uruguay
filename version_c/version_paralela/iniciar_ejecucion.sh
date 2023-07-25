#!/bin/bash

# Se asigna el valor por defecto
NP=${1:-4}
STEPS=${2:-5}

# Se ejecuta mpirun con el valor de NP
module load mpi/mpich-x86_64
python3 -m pip install -r requirements.txt
python3 scripts_python/scriptHost.py
make clean
make
mpirun -np $NP --hostfile hosts_conectables.txt ./predecir_PAD_MPI $STEPS 
