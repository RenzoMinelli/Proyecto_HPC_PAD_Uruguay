import numpy as np
import pandas as pd
import os
import time 
from math import floor
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap
from config import *
from keras.models import load_model

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

# Directorio donde se guardarán las imágenes
directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

cantidad_fuera_del_medidor = 1
ancho_bloque = cantidad_fuera_del_medidor * 2 + 1
cantidadMedidores = 16*16
tamaño_matriz = TAMAÑO_MATRIZ

mascara_cargada = None

def coordenada_en_mascara(x,y):
    global mascara_cargada
    # cargamos mascara matriz desde auxiliar/mascara.csv
    if mascara_cargada is None:
        ruta_completa = os.path.join(DIRECTORIO_AUXILIAR, 'mascara.csv')
        df = pd.read_csv(ruta_completa, header=None)
        mascara_cargada = df.values
    mascara = mascara_cargada
    return mascara[y][x] == 1

def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y


def predecir_por_bloque(steps=5):
    # cargo los modelos en un dict con clave el nombre del archivo
    modelos = {}
    archivos_csv = [f for f in os.listdir(directorio_modelos) if f.endswith('.keras')]
    # archivos_csv = ['0.keras', '1.keras']
    for archivo in archivos_csv:
        print('Procesando modelo nombre: ' + archivo)
        ruta_completa = os.path.join(directorio_modelos, archivo)

        modelo = load_model(ruta_completa)
        modelos[archivo[:-6]] = modelo

    print("modelos cargados: ", modelos.keys())
    # ahora voy a predecir el siguiente valor para cada medidor
    # voy a guardar las predicciones en una matriz de 16 x 16, cada posicion es la predicion de un medidor
    # y luego graficaré un mapa de calor con esa matriz

    # cargo los matrices por medidor
    directorio_matrices = DIRECTORIO_CSVS_MATRICES_GENERADAS
    archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
    matrices = {}
    for archivo in archivos_csv:
        print('Procesando archivo: ' + archivo)
        ruta_completa = os.path.join(directorio_matrices, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices[archivo[:-4]] = df.values

    ruta_al_archivo = DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA
    
    for k in range(steps):
        print("----- Paso: ", k)
        predicciones = np.zeros(tamaño_matriz)
        for i in range(16):
            for j in range(16):

                if not coordenada_en_mascara(j, i):
                    continue

                numMedidor = i * 16 + j 
                # obtengo el nombre del archivo
                clave = str(numMedidor)
                # obtengo el modelo
                modelo = modelos[clave]
                # hago la prediccion con las ultimas 12 filas de la matriz
                df = pd.DataFrame(matrices[clave][-12:,:]).drop(columns=[0])
                lista = df.values
                bloque = lista.reshape(1, -1, 3, 3, 1)

                # predigo
                prediccion = modelo.predict(bloque)
                # guardo la prediccion
                predicciones[i, j] = prediccion[0,0]

        # Guardar la matriz en un archivo CSV
        nombre_archivo = f"matriz_prediccion_step_{k}.csv"
        guardar_matriz(predicciones, ruta_al_archivo, nombre_archivo)

        # ahora voy a graficar un mapa de calor con las predicciones  
        # si k tiene una cifra le ponemos un 0 antes
        aux = ""
        if k < 10:
            aux = "0" + str(k)
        else:
            aux = str(k)

        nombre_imagen = f"imagen_prediccion_step_{aux}.png"
        crear_heatmap(predicciones,directorio_guardado,nombre_imagen, "Prediccion Step " + str(k))
            

        fila = np.zeros(ancho_bloque*ancho_bloque + 1)
        fila[0] = time.time()

        # print("Fila: ", fila)
        for numMedidor in range(0, cantidadMedidores):
            # obtengo los indices de la matriz para ese bloque
            medidor_x, medidor_y = convertir_medidor_a_cord(numMedidor)

            if not coordenada_en_mascara(medidor_x, medidor_y):
                continue

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
                        valor = predicciones[posMatrizY_orig][posMatrizX_orig]
                        # sumo 1 porque en la 0 ponemos el tiempo
                        fila[numMedidorFila + 1] = valor
                    else:
                        # si esta fuera de la matriz original, pongo un 0
                        fila[numMedidorFila + 1] = 0
            # agrego la fila a la matriz del medidor numMedidor

            matrices[str(numMedidor)] = np.vstack((matrices[str(numMedidor)], fila))

if __name__ == "__main__":
    predecir_por_bloque()