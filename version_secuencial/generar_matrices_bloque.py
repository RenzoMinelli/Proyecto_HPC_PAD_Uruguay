import pandas as pd
import numpy as np
import os
from math import floor

from config import *
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap

def aplicar_mascara_a_matriz(matriz):
    # cargamos mascara matriz desde auxiliar/mascara.csv
    ruta_completa = os.path.join(DIRECTORIO_AUXILIAR, 'mascara.csv')
    df = pd.read_csv(ruta_completa, header=None)
    mascara = df.values
    matriz_resultado = np.zeros(TAMAÑO_MATRIZ)

    # revisamos para las posiciones de la mascara, si hay un 1
    # vemos en la matriz, si hay valor dejamos ese valor, sino ponemos un promedio de los 4 valores de alrededor

    for i in range(0, TAMAÑO_MATRIZ[0]):    
        for j in range(0, TAMAÑO_MATRIZ[1]):
            if mascara[i][j] == 1:
                if matriz[i][j] != 0:
                    matriz_resultado[i][j] = matriz[i][j]
                else:
                    print("La posicion ", i, j, " tiene valor 0. Calculando promedio")
                    # promedio de los 4 valores de alrededor
                    suma = 0
                    cantidad = 0
                    if i > 0:
                        suma += matriz[i-1][j]
                        cantidad += 1
                    if i < TAMAÑO_MATRIZ[0] - 1:
                        suma += matriz[i+1][j]
                        cantidad += 1
                    if j > 0:
                        suma += matriz[i][j-1]
                        cantidad += 1
                    if j < TAMAÑO_MATRIZ[1] - 1:
                        suma += matriz[i][j+1]
                        cantidad += 1
                    matriz_resultado[i][j] = suma / cantidad
    return matriz_resultado
    
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


# latitud vertical, longitud horizontal
# dado un par de coordenadas latitud longitud, devuelve la coordenada en la matriz (x e y)

def convertir_latlong_a_cord(latitud,longitud):

    latitud = round(latitud, 2)
    longitud = round(longitud, 2)

    lat_min = -30.33
    lat_max = -34.7
    
    long_max = -53.4
    long_min = -58.33

    # queremos que x sea entero este entre 0 y 15
    # queremos que y sea entero este entre 1 y 14

    y = int((latitud - lat_min) / (lat_max - lat_min) * 14) + 1
    x = int((longitud - long_min) / (long_max - long_min) * 15) 

    return x,y

# numero de medidor va desde 0 hasta 255
# dar coordenads x e y
def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

def generar_matrices_bloque():

    # Define el tamaño de la matriz
    tamaño_matriz = TAMAÑO_MATRIZ

    # Lugar donde se encuentran tus archivos CSV
    directorio_csvs = DIRECTORIO_CSVS_DATOS

    archivos_csv = [f for f in os.listdir(directorio_csvs) if f.endswith('.csv')]


    # Una lista para almacenar todas las matrices
    matrices = {}

    # Leer cada archivo CSV y generar la matriz para cada instante de tiempo
    for archivo in archivos_csv:

        print('Procesando archivo: ' + archivo)

        ruta_completa = os.path.join(directorio_csvs, archivo)
        df = pd.read_csv(ruta_completa)

        # los archivos se llaman inia_gras_pad2006.csv, el año son los ultimos 4 digitos
        anio = archivo[-8:-4]
        # Para cada columna del archivo CSV del formato anio_mmd, genera una matriz para ese instante
        for columna in df.columns:
        
            print('Procesando columna: ' + columna)
            # si el nombre de la columna es anio_mmd (donde mm y d son numeros, d entre 1 y 3)
            if columna.startswith(anio) and (columna.endswith('1') or columna.endswith('2') or columna.endswith('3')):

                # Genero una matriz para toda esta columna
                matriz = np.zeros(tamaño_matriz)

                # para cada fila de la columna
                for index, row in df.iterrows():
                    # obtengo las coordenadas de la fila
                    latitud = row['Latitud']
                    longitud = row['Longitud']
                    # obtengo la coordenada en la matriz
                    x,y = convertir_latlong_a_cord(latitud,longitud)
                    # obtengo el valor de la columna
                    valor = row[columna]
                    # asigno el valor a la matriz
                    matriz[y][x] = valor

                # matriz = aplicar_mascara_a_matriz(matriz)
                nombre_matriz = f"imagen_{columna}.csv"
                guardar_matriz(matriz,DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA,nombre_matriz)
                
                # agrego la matriz al dict con clave el nombre de la columna
                matrices[columna] = matriz

    # Ahora agarramos las matrices y generamos una matriz para cada bloque 2x2

    directorio_matrices_bloque = DIRECTORIO_CSVS_MATRICES_GENERADAS
    cantidadMedidores = 16*16
    cantidad_fuera_del_medidor = 1 # (bloques 3 x 3, o sea 1 central más 1 de cada lado)
    # entrenamos un modelo por cada medidor, tomando un vecindario de 3x3 para entrenar los modelos
    for numMedidor in range(0, cantidadMedidores):
        # obtengo los indices de la matriz para ese bloque
        medidor_x, medidor_y = convertir_medidor_a_cord(numMedidor)

        ancho_bloque = cantidad_fuera_del_medidor * 2 + 1

        # print("Medidor: ", numMedidor, " x: ", medidor_x, " y: ", medidor_y)
        # genero la matriz que voy a guardar al final 5 columnas: tiempo, medicio1, medicion2, medicion3, medicion4
        matriz = np.zeros((0, ancho_bloque*ancho_bloque + 1))
        
        # obtengo el bloque de cada matriz
        for clave in matrices.keys():
            # print('Procesando clave: ' + clave)
            # obtengo la matriz
            matriz_original = matrices[clave]
            
            tiempo = clave
            fila = np.zeros(ancho_bloque*ancho_bloque + 1)
            fila[0] = tiempo

            # print("Fila: ", fila)

            for i in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
                for j in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
                    posMatrizX_orig = i + medidor_x
                    posMatrizY_orig = j + medidor_y

                    numMedidorLocalX = i + cantidad_fuera_del_medidor
                    numMedidorLocalY = j + cantidad_fuera_del_medidor
                    numMedidorFila = numMedidorLocalY * ancho_bloque + numMedidorLocalX

                    # print("i: ", i, " j: ", j, " posMatrizX_orig: ", posMatrizX_orig, " posMatrizY_orig: ", posMatrizY_orig, " numMedidorLocalX: ", numMedidorLocalX, " numMedidorLocalY: ", numMedidorLocalY, " numMedidorFila: ", numMedidorFila, "\n")
                    # si la posicion esta dentro de la matriz original
                    if posMatrizX_orig >= 0 and posMatrizX_orig < tamaño_matriz[0] and posMatrizY_orig >= 0 and posMatrizY_orig < tamaño_matriz[1]:
                        # obtengo el valor de la matriz original
                        valor = matriz_original[posMatrizX_orig, posMatrizY_orig]
                        # sumo 1 porque en la 0 ponemos el tiempo
                        fila[numMedidorFila + 1] = valor / 100 # divido por 100 para normalizar
                    else:
                        # si esta fuera de la matriz original, pongo un 0
                        fila[numMedidorFila + 1] = 0
            
            matriz = np.vstack((matriz, fila))

        # genero el archivo csv
        print('Generando archivo de medidor: ' + str(numMedidor))
        ruta_completa = os.path.join(directorio_matrices_bloque, str(numMedidor) + '.csv') 
        df = pd.DataFrame(matriz)
        df.to_csv(ruta_completa, header=None, index=None)


def generar_imagenes_matrices_anteriores():
    
    directorio_csvs = DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA
    directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

    i = 0
    for f in os.listdir(directorio_csvs):
        archivos_csv = f
        # ahora voy a graficar un mapa de calor con las predicciones      
        nombre_imagen = f"imagen_{archivos_csv}.png"

        df = pd.read_csv(directorio_csvs+archivos_csv, header=None)
        crear_heatmap(df,directorio_guardado,nombre_imagen)
        i += 1 
        print("generada imagen " , archivos_csv)

if __name__ == "__main__":
    generar_matrices_bloque()
    generar_imagenes_matrices_anteriores()
