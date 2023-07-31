import numpy as np
import pandas as pd
import os
from CustomModel import create_model
from config import *
import sys 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

def save_model(model, filename):
    model.save(filename)

def procesar_archivos(archivo):

    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    clave = archivo[:-4]

    cols = list(df)[1:] # las columnas que vamos a usar para entrenamineto es todo menos la primera
    df_for_training = df[cols].astype(float)

    n_future = 1 # cuantos pasos al futuro predecir 
    n_past = PASOS_ATRAS_PARA_PREDICCION # cuantos pasos al pasado mirar
    df_for_training = df_for_training.values

    #Empty lists to be populated using formatted training data
    trainX = []
    trainY = []

    ancho_bloque = RADIO_BLOQUE * 2 + 1
    pos_a_predecir = int((ancho_bloque^2 - 1) / 2)
    for i in range(n_past, len(df_for_training) - n_future +1):
        trainX.append(df_for_training[i - n_past:i, 0:df_for_training.shape[1]])
        trainY.append(df_for_training[i + n_future - 1:i + n_future, pos_a_predecir])

    trainX, trainY = np.array(trainX), np.array(trainY)

    model = create_model(trainX, trainY)

    # fit the model
    history = model.fit(trainX, trainY, epochs=5, batch_size=16, verbose=1)

    nombre_archivo = clave + '.keras'
    save_model(model, directorio_modelos + nombre_archivo) 

if __name__ == "__main__":
    archivo = sys.argv[1]
    procesar_archivos(archivo)
