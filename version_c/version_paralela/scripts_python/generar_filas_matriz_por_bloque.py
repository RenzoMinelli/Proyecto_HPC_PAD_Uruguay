import numpy as np
import pandas as pd
import os
import time 
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
    ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    matriz = df.values

    # obtengo los datos del bloque del medidor y armo la fila
    medidor_x,medidor_y = convertir_medidor_a_cord(numMedidor)
    fila = np.zeros(ancho_bloque*ancho_bloque + 1)
    fila[0] = time.time()

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
                valor = matriz[posMatrizY_orig][posMatrizX_orig]
                # sumo 1 porque en la 0 ponemos el tiempo
                fila[numMedidorFila + 1] = valor
            else:
                # si esta fuera de la matriz original, pongo un 0
                fila[numMedidorFila + 1] = 0

    # agrego la fila a la matriz del medidor numMedidor
    clave = str(numMedidor)
    # leemos el archivo calve.csv y le armamos la fila
    ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, clave + '.csv')
    df = pd.read_csv(ruta_completa, header=None)

    nueva_fila = pd.DataFrame(fila.reshape(-1, len(fila)))
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(ruta_completa, header=None, index=False)

if __name__ == "__main__":
    archivo = sys.argv[1]
    numMedidor = int(sys.argv[2])
    generar_filas_matriz_por_bloque(archivo, numMedidor)