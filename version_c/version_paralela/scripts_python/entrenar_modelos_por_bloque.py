import numpy as np
import pandas as pd
import os
from CustomModel import create_model
from config import *
import multiprocessing as mp
from math import ceil
import sys 

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

def save_model(model, filename):
    model.save(filename)

def procesar_archivos(archivo):

    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    clave = archivo[:-4]
    matriz = df.values
    # elimino la primera columna

    datos = matriz[:, 1:]
    etiquetas = datos[1:, 4]
    datos = datos[:-1, :]

    train_X = datos[:-100]  # Usa todos los ejemplos menos los últimos 101 para entrenamiento
    train_y = etiquetas[:-100]  # Usa todas las etiquetas menos las últimas 100 para entrenamiento

    test_X = datos[-100:]  # Usa los últimos 101 ejemplos menos el último para prueba
    test_y = etiquetas[-100:]

    modelo = create_model(input_shape=(None, 9))
    modelo.fit(train_X, train_y, epochs=80, validation_data=(test_X, test_y))

    nombre_archivo = clave + '.keras'
    save_model(modelo, directorio_modelos + nombre_archivo)
        

if __name__ == "__main__":
    archivo = sys.argv[1]
    procesar_archivos(archivo)
