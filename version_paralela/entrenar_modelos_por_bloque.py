import numpy as np
import pandas as pd
import os
from ConvLSTM import create_model
from config import *
import multiprocessing as mp

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

def save_model(model, filename):
    model.save(filename)

def entrenar_modelos_por_bloque():
    directorio_matrices = DIRECTORIO_CSVS_MATRICES_GENERADAS

    # cargo todas las matrices en un dict con clave el nombre del archivo
    archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
    cantidad_archivos = len(archivos_csv)
    cantidad_archivos_por_proceso = int(cantidad_archivos / NUMERO_DE_PROCESOS)
    procesos = []
    for nro_proceso in range(NUMERO_DE_PROCESOS):
        primer_archivo = nro_proceso * cantidad_archivos_por_proceso
        ultimo_archivo = min(primer_archivo + cantidad_archivos_por_proceso,cantidad_archivos)
        archivos = archivos_csv[primer_archivo:ultimo_archivo]
        procesos.append(mp.Process(target=procesar_archivos, args=(archivos,)))

    for p in procesos:
        p.start()

    for proceso in procesos:
        proceso.join()

def procesar_archivos(archivos):

    process = mp.current_process()
    pid = process.pid

    for archivo in archivos:
        print('Proceso: ',pid, ' Procesando archivo: ' + archivo)
        ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        clave = archivo[:-4]
        matriz = df.values
        # elimino la primera columna
        matriz = matriz[:, 1:]
        datos = matriz.reshape(-1, 1, 3, 3, 1)
        etiquetas = datos[1:, 0, 1, 1, 0]

        train_X = datos[:-101]  # Usa todos los ejemplos menos los últimos 101 para entrenamiento
        train_y = etiquetas[:-100]  # Usa todas las etiquetas menos las últimas 100 para entrenamiento
        test_X = datos[-101:-1]  # Usa los últimos 101 ejemplos menos el último para prueba
        test_y = etiquetas[-100:]

        modelo = create_model(input_shape=(None, 3, 3, 1))
        modelo.fit(train_X, train_y, epochs=80, validation_data=(test_X, test_y))

        nombre_archivo = clave + '.h5'
        save_model(modelo, directorio_modelos + nombre_archivo)

if __name__ == "__main__":
    entrenar_modelos_por_bloque()
