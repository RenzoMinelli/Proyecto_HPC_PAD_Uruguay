import numpy as np
import pandas as pd
import os
import torch
import matplotlib.pyplot as plt
import seaborn as sns
import time 
from math import floor 
from PIL import Image
from config import *
from keras.models import load_model

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

# Directorio donde se guardarán las imágenes
directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

cantidad_fuera_del_medidor = 1
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
    archivos_csv = [f for f in os.listdir(directorio_modelos) if f.endswith('.h5')]
    # archivos_csv = ['0.h5', '1.h5']
    for archivo in archivos_csv:
        print('Procesando modelo nombre: ' + archivo)
        ruta_completa = os.path.join(directorio_modelos, archivo)

        modelo = load_model(ruta_completa)
        modelos[archivo[:-3]] = modelo

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

    for k in range(steps):
        print("----- Paso: ", k)
        predicciones = np.zeros(tamaño_matriz)
        for i in range(16):
            for j in range(16):
                numMedidor = i * 16 + j 
                # obtengo el nombre del archivo
                clave = str(numMedidor)
                # obtengo el modelo
                modelo = modelos[clave]
                # hago la prediccion con las ultimas 12 filas de la matriz
                df = pd.DataFrame(matrices[clave][:,-12:]).drop(columns=[0])
                lista = df.values
                bloque = lista.reshape(-1, 1, 3, 3, 1)

                # predigo
                prediccion = modelo.predict(bloque)
                # guardo la prediccion
                predicciones[i, j] = prediccion[0,0]

        # ahora voy a graficar un mapa de calor con las predicciones
        #plt.figure(figsize=(10, 10))
        #imagen1 = Image.open("./version_secuencial/auxiliar/Mapa_uruguay.jpg")
        
        fig, ax = plt.subplots()
        sns.heatmap(predicciones,  annot=True,fmt='.1f', cmap='coolwarm', ax=ax ,alpha=0.5)
        imagen2 = Image.open("./version_secuencial/auxiliar/Mapa_uruguay.jpg")
        imagen2 = np.array(imagen2)
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        ax.imshow(imagen2, extent=[xmin, xmax, ymin, ymax], alpha=0.5)
        
        nombre_imagen = f"imagen_{k}.png"

        ruta_guardado = os.path.join(directorio_guardado, nombre_imagen)
        plt.savefig(ruta_guardado)


            
        # Limpiar el gráfico para generar la siguiente imagen
        #plt.savefig
        #plt.show()       
        plt.clf()    
    

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
