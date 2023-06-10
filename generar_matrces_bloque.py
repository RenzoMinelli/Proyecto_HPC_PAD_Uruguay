import pandas as pd
import numpy as np
import os
from math import floor

# recibe el numero de bloque y devuelve 4 valores, x_desde, x_hasta, y_desde, y_hasta
# hay 8 bloques en cada eje
def num_bloque_posiciones_matriz(num):
    index_y = floor(num / 8)
    index_x = num % 8
    x_desde = index_x * 2
    x_hasta = x_desde + 2
    y_desde = index_y * 2
    y_hasta = y_desde + 2
    return x_desde, x_hasta, y_desde, y_hasta

# cargamos las matrices que son csv, y las guardamos en un diccionario con el nombre como clave
directorio_matrices = './matrices_por_instante/'
matrices = {}
archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
for archivo in archivos_csv:
    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(directorio_matrices, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    matrices[archivo[:-4]] = df.values

# Ahora agarramos las matrices y generamos una matriz para cada bloque 2x2

directorio_matrices_bloque = './matrices_bloque/'
cantidadBloques = 64

for numBloque in range(0, cantidadBloques):
    # obtengo los indices de la matriz para ese bloque
    x_desde, x_hasta, y_desde, y_hasta = num_bloque_posiciones_matriz(numBloque)

    # genero la matriz que voy a guardar al final 5 columnas: tiempo, medicio1, medicion2, medicion3, medicion4
    matriz = np.zeros((len(matrices.keys()), 5))
    
    # obtengo el bloque de cada matriz
    for clave in matrices.keys():
        print('Procesando clave: ' + clave)
        # obtengo la matriz
        matriz_original = matrices[clave]
        # obtengo el bloque
        bloque = matriz_original[x_desde:x_hasta, y_desde:y_hasta]
        
        tiempo = clave
        medicio1 = bloque[0,0]
        medicio2 = bloque[0,1]
        medicio3 = bloque[1,0]
        medicio4 = bloque[1,1]

        # agrego una fila a la matriz [tiempo, medicio1, medicio2, medicio3, medicio4]
        nueva_fila = np.array([tiempo, medicio1, medicio2, medicio3, medicio4])
        matriz = np.vstack([matriz, nueva_fila])

    # genero el archivo csv
    print('Generando archivo: ' + str(numBloque))
    ruta_completa = os.path.join(directorio_matrices_bloque, str(numBloque) + '.csv') 
    df = pd.DataFrame(matriz)
    df.to_csv(ruta_completa, header=None, index=None)
