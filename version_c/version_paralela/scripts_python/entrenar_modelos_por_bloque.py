import numpy as np
import pandas as pd
import os
from CustomModel import create_model
from config import *
import sys 

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

def save_model(model, filename):
    model.save(filename)

def procesar_archivos(archivo):

    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    clave = archivo[:-4]

    train_dates = pd.to_datetime(df[0]) # la primera columna es la fecha
    cols = list(df)[1:] # las columnas que vamos a usar para entrenamineto es todo menos la primera
    df_for_training = df[cols].astype(float)

    n_future = 1 # cuantos pasos al futuro predecir 
    n_past = 14 # cuantos pasos al pasado mirar
    df_for_training = df_for_training.values

    #Empty lists to be populated using formatted training data
    trainX = []
    trainY = []

    n_future = 1   # Number of days we want to look into the future based on the past days.
    n_past = 14  # Number of past days we want to use to predict the future.

    pos_a_predecir = 4
    for i in range(n_past, len(df_for_training) - n_future +1):
        trainX.append(df_for_training[i - n_past:i, 0:df_for_training.shape[1]])
        trainY.append(df_for_training[i + n_future - 1:i + n_future, pos_a_predecir])

    trainX, trainY = np.array(trainX), np.array(trainY)

    # guardar trainX 
    direccion_trainX = os.path.join(DIRECTORIO_TRAINING_DATA, clave + '.npy')
    np.save(direccion_trainX, trainX)

    model = create_model(trainX, trainY)

    # fit the model
    history = model.fit(trainX, trainY, epochs=5, batch_size=16, validation_split=0.1, verbose=1)

    nombre_archivo = clave + '.keras'
    save_model(model, directorio_modelos + nombre_archivo) 

if __name__ == "__main__":
    archivo = sys.argv[1]
    procesar_archivos(archivo)
