import numpy as np
import pandas as pd
import os
import time 
from math import floor, ceil
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap
from config import *
from keras.models import load_model
import multiprocessing as mp
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

def predecir_modelo(archivo):
    print(f"Procesando {archivo}")
    ruta_completa = os.path.join(directorio_modelos, archivo)
    num_modelo = archivo[:-6]
    modelo = load_model(ruta_completa)

    ruta_completa_matriz = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, num_modelo + '.csv')
    df = pd.read_csv(ruta_completa_matriz, header=None)
    matriz = df.values

    df = pd.DataFrame(matriz[-1:,:]).drop(columns=[0])
    lista = df.values
    bloque = lista.reshape(1, 9)
    # predigo
    prediccion = modelo.predict(bloque, verbose=None)
    prediccion = prediccion[0,0]
    print(prediccion)
    

if __name__ == "__main__":
    archivo = sys.argv[1]
    predecir_modelo(archivo)
