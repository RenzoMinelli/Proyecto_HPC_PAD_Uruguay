import numpy as np
import pandas as pd
import os
from math import floor
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from config import *
from keras.models import load_model
import sys

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

# Directorio donde se guardarán las imágenes
directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

cantidad_fuera_del_medidor = 1
ancho_bloque = cantidad_fuera_del_medidor * 2 + 1
cantidadMedidores = 16*16
tamaño_matriz = TAMAÑO_MATRIZ

def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

mascara_cargada = None
def coordenada_en_mascara(x,y):
    global mascara_cargada
    # cargamos mascara matriz desde auxiliar/mascara.csv
    if mascara_cargada is None:
        ruta_completa = os.path.join(DIRECTORIO_AUXILIAR, 'mascara.csv')
        df = pd.read_csv(ruta_completa, header=None)
        mascara_cargada = df.values
    mascara = mascara_cargada
    return mascara[y][x] == 1

def predecir_modelo(archivo, step=1):
    # print(f"Procesando {archivo}")
    ruta_completa = os.path.join(directorio_modelos, archivo)
    num_modelo = archivo[:-6]
    model = load_model(ruta_completa)
    
    n_days_for_prediction = step # cuantos pasos predecir

    # cargo la training data 
    prediccion = 0
    direccion_trainX = os.path.join(DIRECTORIO_TRAINING_DATA, num_modelo + '.npy')
    with open(direccion_trainX, 'rb') as f:
        trainX = np.load(f)
        prediccion = model.predict(trainX[-n_days_for_prediction:], verbose=None)

    # guardamos la matriz de predicciones para todos los steps
    predicciones = pd.DataFrame(prediccion)
    guardar_matriz(predicciones, DIRECTORIO_PREDICCIONES, num_modelo + '.csv')

if __name__ == "__main__":
    archivo = sys.argv[1]
    step = int(sys.argv[2])
    predecir_modelo(archivo, step)
