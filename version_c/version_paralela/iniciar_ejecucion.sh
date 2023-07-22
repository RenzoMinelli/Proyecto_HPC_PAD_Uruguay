#!/bin/bash

# Se asigna el valor por defecto
NP=${1:-4}

# Se ejecuta mpirun con el valor de NP
mpirun -np $NP ./predecir_PAD_MPI
