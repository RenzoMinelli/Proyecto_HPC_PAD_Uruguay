import pandas as pd
import numpy as np
import os
import sys 
from math import floor
from config import *

def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

def generar_matrices_bloque(numMedidor, steps_para_evaluacion):
             
    # cargamos las matrices de los csvs
    matrices = {}
    for archivo in os.listdir(DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES):
        if archivo.endswith(".csv"):
            ruta_completa = os.path.join(DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES, archivo)
            df = pd.read_csv(ruta_completa, header=None)
            clave = archivo.split('.')[0]
            
            anio = clave[0:4]
            mes = clave[5:-1]
            trimestre = clave[-1:]
            if mes == '02':
                dia = '28'
            else:
                dia = trimestre + '0'
            
            clave = anio + '-' + mes + '-' + dia

            matrices[clave] = df.values

    # Ahora agarramos las matrices y generamos una matriz para cada bloque 2x2

    directorio_matrices_bloque = DIRECTORIO_CSVS_MATRICES_GENERADAS
    cantidad_fuera_del_medidor = 1 # (bloques 3 x 3, o sea 1 central más 1 de cada lado)
    # entrenamos un modelo por cada medidor, tomando un vecindario de 3x3 para entrenar los modelos
    
    # obtengo los indices de la matriz para ese bloque
    medidor_x, medidor_y = convertir_medidor_a_cord(numMedidor)

    ancho_bloque = cantidad_fuera_del_medidor * 2 + 1

    # print("Medidor: ", numMedidor, " x: ", medidor_x, " y: ", medidor_y)
    # genero la matriz que voy a guardar al final 5 columnas: tiempo, medicio1, medicion2, medicion3, medicion4
    matriz = np.zeros((0, ancho_bloque*ancho_bloque + 1))
    matriz = pd.DataFrame(matriz)

    # definir las columnas
    columnas = ['tiempo', 'medicion1', 'medicion2', 'medicion3', 'medicion4', 'medicion5', 'medicion6', 'medicion7', 'medicion8', 'medicion9' ]
    matriz.columns = columnas

    # obtengo el bloque de cada matriz
    for clave in matrices.keys():
        matriz_original = matrices[clave]
        tiempo = clave
        fila = pd.Series([0]*len(matriz.columns), index=matriz.columns)
        fila['tiempo'] = pd.to_datetime(tiempo, format='%Y-%m-%d')

        for i in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
            for j in range(cantidad_fuera_del_medidor*-1, cantidad_fuera_del_medidor+1):
                posMatrizX_orig = i + medidor_x
                posMatrizY_orig = j + medidor_y

                numMedidorLocalX = i + cantidad_fuera_del_medidor
                numMedidorLocalY = j + cantidad_fuera_del_medidor
                numMedidorFila = numMedidorLocalY * ancho_bloque + numMedidorLocalX

                if posMatrizX_orig >= 0 and posMatrizX_orig < TAMAÑO_MATRIZ[0] and posMatrizY_orig >= 0 and posMatrizY_orig < TAMAÑO_MATRIZ[1]:
                    valor = matriz_original[posMatrizY_orig][posMatrizX_orig]
                    fila[numMedidorFila + 1] = valor  
                else:
                    fila[numMedidorFila + 1] = 0

        matriz.loc[len(matriz)] = fila

    # genero el archivo csv
    print('Generando archivo de medidor: ' + str(numMedidor))
    ruta_completa = os.path.join(directorio_matrices_bloque, str(numMedidor) + '.csv') 
    # sortear por fecha
    matriz = matriz.sort_values(by=['tiempo'])
    # sacamos las ultimas steps_para_evaluacion filas 
    matriz = matriz[:-steps_para_evaluacion]
    matriz.to_csv(ruta_completa, header=None, index=None)

def coordenada_en_mascara(x,y):
    ruta_completa = os.path.join(DIRECTORIO_AUXILIAR, 'mascara.csv')
    df = pd.read_csv(ruta_completa, header=None)
    mascara = df.values
    return mascara[y][x] == 1

if __name__ == "__main__":
    numMedidor = int(sys.argv[1])
    steps_para_evaluacion = int(sys.argv[2])
    generar_matrices_bloque(numMedidor, steps_para_evaluacion)
