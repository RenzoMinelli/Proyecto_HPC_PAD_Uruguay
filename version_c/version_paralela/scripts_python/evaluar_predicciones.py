import numpy as np
import pandas as pd
import os
from config import *
import sys 
import matplotlib.pyplot as plt
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def evaluar_predicciones(steps_a_evaluar, epochs):

    matrices_valores_reales = {}
    directorio_matrices_reales = DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES

    archivos = sorted(os.listdir(directorio_matrices_reales))[-steps_a_evaluar:]
    indice = 0
    for archivo in archivos:
        ruta_completa = os.path.join(directorio_matrices_reales, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices_valores_reales[indice] = df
        indice += 1

    direccion_matrices_predicciones = DIRECTORIO_MATRICES_PREDICCIONES
    matrices_predicciones = {}
    archivos = sorted(os.listdir(direccion_matrices_predicciones))[-steps_a_evaluar:]
    indice = 0
    for archivo in archivos:
        ruta_completa = os.path.join(direccion_matrices_predicciones, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices_predicciones[indice] = df
        indice += 1

    errores = []
    for i in range(steps_a_evaluar):
        matriz_real = matrices_valores_reales[i]
        matriz_prediccion = matrices_predicciones[i]
        diferencia = matriz_real.values - matriz_prediccion.values
        suma = np.sum(diferencia)
        suma = abs(suma)
        errores.append(suma)

    # Tracing the averages
    plt.plot(errores)
    plt.xlabel('Pasos')
    plt.ylabel('Suma de errores de la prediccion para cada medidor')

    # Saving the plot as an image
    fecha_hora_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nombre_imagen = f'grafico_epochs_{epochs}_{fecha_hora_actual}.png'
    plt.savefig(nombre_imagen)
        
if __name__ == "__main__":
    steps_a_evaluar = int(sys.argv[1])
    epochs = int(sys.argv[2])
    evaluar_predicciones(steps_a_evaluar, epochs)
