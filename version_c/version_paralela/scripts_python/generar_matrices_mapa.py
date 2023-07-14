import pandas as pd
import numpy as np
import os
from config import *
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import convertir_latlong_a_cord

def generar_matriz_mapa(archivo):

    print('Procesando archivo: ' + archivo)

    ruta_completa = os.path.join(DIRECTORIO_CSVS_DATOS, archivo)
    df = pd.read_csv(ruta_completa)
    latitud = df['Latitud']
    longitud = df['Longitud']
    # obtengo la coordenada en la matriz
    x,y = convertir_latlong_a_cord(latitud,longitud)

    # los archivos se llaman inia_gras_pad2006.csv, el año son los ultimos 4 digitos
    anio = archivo[-8:-4]
    # Para cada columna del archivo CSV del formato anio_mmd, genera una matriz para ese instante
    for columna in df.columns:
    
        print('Procesando columna: ' + columna)
        # si el nombre de la columna es anio_mmd (donde mm y d son numeros, d entre 1 y 3)
        if columna.startswith(anio) and (columna.endswith('1') or columna.endswith('2') or columna.endswith('3')):

            # Genero una matriz para toda esta columna
            matriz = np.zeros(TAMAÑO_MATRIZ)

            # para cada fila de la columna
            for index, row in df.iterrows():
                # obtengo el valor de la columna
                valor = row[columna]
                # asigno el valor a la matriz
                matriz[y][x] = valor / 100

            # matriz = aplicar_mascara_a_matriz(matriz)
            nombre_matriz = f"{columna}.csv"

            # creates a .csv file in the directory DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA with the name nombre_matriz
            # that csv file contains the matrix
            guardar_matriz(matriz,DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES,nombre_matriz)

if __name__ == "__main__":
    generar_matriz_mapa()
