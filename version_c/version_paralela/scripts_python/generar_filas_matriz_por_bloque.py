import numpy as np
import pandas as pd
import os
import datetime 
from math import floor
from config import *
import multiprocessing as mp
import sys

cantidad_fuera_del_medidor = 1
ancho_bloque = cantidad_fuera_del_medidor * 2 + 1

def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

def generar_filas_matriz_por_bloque(archivo, numMedidor):
    # cargamos la matriz de predicciones 
    clave = str(numMedidor)

    ruta_completa = os.path.join(DIRECTORIO_MATRICES_PREDICCIONES, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    matriz_predicciones = df

    # cargamos la matriz donde vamos a poner los datos
    ruta_completa_bloque = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, clave + '.csv')
    matriz = pd.read_csv(ruta_completa_bloque, header=None)
    matriz[0] = pd.to_datetime(matriz[0])

    # definir las columnas
    columnas = ['tiempo', 'medicion1', 'medicion2', 'medicion3', 'medicion4', 'medicion5', 'medicion6', 'medicion7', 'medicion8', 'medicion9' ]
    matriz.columns = columnas

    # obtengo los datos del bloque del medidor y armo la fila
    medidor_x,medidor_y = convertir_medidor_a_cord(numMedidor)
    fila = pd.Series([0]*len(matriz.columns), index=matriz.columns)
    fila['tiempo'] = pd.to_datetime(datetime.datetime.now())

    for i in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
        for j in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
            posMatrizX_orig = i + medidor_x
            posMatrizY_orig = j + medidor_y

            numMedidorLocalX = i + cantidad_fuera_del_medidor
            numMedidorLocalY = j + cantidad_fuera_del_medidor
            numMedidorFila = numMedidorLocalY * ancho_bloque + numMedidorLocalX

            # print("i: ", i, " j: ", j, " posMatrizX_orig: ", posMatrizX_orig, " posMatrizY_orig: ", posMatrizY_orig, " numMedidorLocalX: ", numMedidorLocalX, " numMedidorLocalY: ", numMedidorLocalY, " numMedidorFila: ", numMedidorFila, "\n")
            # si la posicion esta dentro de la matriz original
            if posMatrizX_orig >= 0 and posMatrizX_orig < TAMAÑO_MATRIZ[0] and posMatrizY_orig >= 0 and posMatrizY_orig < TAMAÑO_MATRIZ[1]:
                # obtengo el valor de la matriz original
                valor = matriz_predicciones[posMatrizY_orig][posMatrizX_orig]
                # sumo 1 porque en la 0 ponemos el tiempo
                fila[numMedidorFila + 1] = valor
            else:
                # si esta fuera de la matriz original, pongo un 0
                fila[numMedidorFila + 1] = 0

    # agrego la fila a la matriz del medidor numMedidor
    matriz.loc[len(matriz)] = fila
    matriz = matriz.sort_values(by=['tiempo'])
    matriz.to_csv(ruta_completa_bloque, header=None, index=None)

if __name__ == "__main__":
    archivo = sys.argv[1]
    numMedidor = int(sys.argv[2])
    generar_filas_matriz_por_bloque(archivo, numMedidor)