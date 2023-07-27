import numpy as np
import pandas as pd
import os
from math import floor
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from config import *
from keras.models import load_model
import sys 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

# Directorio donde se guardarán las imágenes
directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

cantidad_fuera_del_medidor = RADIO_BLOQUE
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
    model = load_model(ruta_completa)
    
    n_past = PASOS_ATRAS_PARA_PREDICCION # cuantos pasos al pasado mirar

    # cargo la training data 
    prediccion = 0
    ruta_completa_bloque = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, num_modelo + '.csv')
    df = pd.read_csv(ruta_completa_bloque, header=None)

    cols = list(df)[1:] # las columnas que vamos a usar para entrenamineto es todo menos la primera
    df_for_training = df[cols].astype(float)
    df_for_training = df_for_training.values

    data = []
    posFinal = len(df_for_training) 
    data.append(df_for_training[posFinal - n_past:posFinal, 0:df_for_training.shape[1]])
    data = np.array(data)
    prediccion = model.predict(data)
    data_frame = pd.DataFrame(prediccion)
    guardar_matriz(data_frame, DIRECTORIO_PREDICCIONES, num_modelo + '.csv')

if __name__ == "__main__":
    archivo = sys.argv[1]
    predecir_modelo(archivo)
