import numpy as np
import pandas as pd
import os
from LSTM import LSTM
import torch
import matplotlib.pyplot as plt
import seaborn as sns
import time 
from math import floor 

directorio_modelos = './modelos/'
cantidad_fuera_del_medidor = 2
ancho_bloque = cantidad_fuera_del_medidor * 2 + 1
cantidadMedidores = 16*16
tamaño_matriz = (16,16)
def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y


def predecir_por_bloque(steps=1):
    # cargo los modelos en un dict con clave el nombre del archivo
    modelos = {}
    archivos_csv = [f for f in os.listdir(directorio_modelos) if f.endswith('.pt')]
    for archivo in archivos_csv:
        print('Procesando modelo nombre: ' + archivo)
        ruta_completa = os.path.join(directorio_modelos, archivo)

        modelo = LSTM(ancho_bloque, 100, 1)
        modelo.load_state_dict(torch.load(ruta_completa))
        modelo.eval()

        modelos[archivo[:-3]] = modelo

    print("modelos cargados: ", modelos.keys())
    # ahora voy a predecir el siguiente valor para cada medidor
    # voy a guardar las predicciones en una matriz de 16 x 16, cada posicion es la predicion de un medidor
    # y luego graficaré un mapa de calor con esa matriz

    # cargo los matrices por medidor
    directorio_matrices = './matrices_por_bloque/'
    archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
    matrices = {}
    for archivo in archivos_csv:
        print('Procesando archivo: ' + archivo)
        ruta_completa = os.path.join(directorio_matrices, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices[archivo[:-4]] = df.values

    for numPrediccion in range(steps):
        predicciones = np.zeros((16, 16))
        for i in range(16):
            for j in range(16):
                numMedidor = i * 16 + j 
                # obtengo el nombre del archivo
                clave = str(numMedidor)
                # obtengo el modelo
                print("clave: ", clave)
                modelo = modelos[clave]
                # hago la prediccion con las ultimas 12 filas de la matriz
                df = pd.DataFrame(matrices[clave][:,-12:]).drop(columns=[0])
                lista = df.values.astype(float)
                bloque = torch.FloatTensor(lista)

                # predigo
                prediccion = modelo(bloque)
                # guardo la prediccion
                predicciones[i, j] = prediccion.item()

        # ahora voy a graficar un mapa de calor con las predicciones
        plt.figure(figsize=(10, 10))
        sns.heatmap(predicciones, annot=True, fmt='.1f', cmap='Blues')
        plt.show()

        fila = np.zeros(ancho_bloque*ancho_bloque + 1)
        fila[0] = time.time()

        # print("Fila: ", fila)
        for numMedidor in range(0, cantidadMedidores):
            # obtengo los indices de la matriz para ese bloque
            medidor_x, medidor_y = convertir_medidor_a_cord(numMedidor)

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
                        valor = predicciones[posMatrizX_orig, posMatrizY_orig]
                        # sumo 1 porque en la 0 ponemos el tiempo
                        fila[numMedidorFila + 1] = valor
                    else:
                        # si esta fuera de la matriz original, pongo un 0
                        fila[numMedidorFila + 1] = 0
            # agrego la fila a la matriz del medidor numMedidor

            matrices[str(numMedidor)] = np.vstack((matrices[str(numMedidor)], fila))

if __name__ == "__main__":
    predecir_por_bloque()
