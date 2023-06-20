import numpy as np
import pandas as pd
import os
from ConvLSTM import create_model
from config import *

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

def save_model(model, filename):
    model.save(filename)

def entrenar_modelos_por_bloque():
    directorio_matrices = DIRECTORIO_CSVS_MATRICES_GENERADAS

    # cargo todas las matrices en un dict con clave el nombre del archivo
    matrices = {}
    archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
    for archivo in archivos_csv:
        print('Procesando archivo: ' + archivo)
        ruta_completa = os.path.join(directorio_matrices, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices[archivo[:-4]] = df.values

    # ahora quiero entrenar un modelo para cada bloque
    # voy a guardar los modelos en un dict con clave el nombre del archivo
    for clave in matrices.keys():
        print('Procesando clave: ' + clave)
        # obtengo la matriz
        matriz = matrices[clave]
        # elimino la primera columna
        matriz = matriz[:, 1:]

        # Cambia la forma de los datos para que sean (muestras, tiempo, filas, columnas, canales)
        datos = matriz.reshape(-1, 1, 3, 3, 1)
        
        # Las etiquetas son los valores centrales de los bloques 3x3 del siguiente paso de tiempo
        etiquetas = datos[1:, 0, 1, 1, 0]  # Asume que quieres predecir el valor central del bloque siguiente en la secuencia

        # Divide los datos en entrenamiento y prueba
        train_X = datos[:-101]  # Usa todos los ejemplos menos los últimos 101 para entrenamiento
        train_y = etiquetas[:-100]  # Usa todas las etiquetas menos las últimas 100 para entrenamiento
        test_X = datos[-101:-1]  # Usa los últimos 101 ejemplos menos el último para prueba
        test_y = etiquetas[-100:]  # Usa las últimas 100 etiquetas para prueba

        # Entrena el modelo
        modelo = create_model(input_shape=(None, 3, 3, 1))
        modelo.fit(train_X, train_y, epochs=80, validation_data=(test_X, test_y))

        nombre_archivo = clave + '.h5'
        save_model(modelo, directorio_modelos + nombre_archivo)


if __name__ == "__main__":
    entrenar_modelos_por_bloque()
