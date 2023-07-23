#!/bin/bash

# Se asigna el valor por defecto
NP=${1:-4}
STEPS=${2:-5}

# Se ejecuta mpirun con el valor de NP
make clean
make
mpirun -np $NP ./predecir_PAD_MPI $STEPS
