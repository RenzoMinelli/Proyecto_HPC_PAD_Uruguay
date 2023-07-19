import numpy as np
import pandas as pd
import os
from math import floor
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap
from config import *
import sys

def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

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

def armar_prediccion(step):
    predicciones = np.zeros(TAMAÑO_MATRIZ)
    # por cada archivo en DIRECTORIO_PREDICCIONES
    for archivo in os.listdir(DIRECTORIO_PREDICCIONES):
        numMedidor = int(archivo[:-4])
        x,y = convertir_medidor_a_cord(numMedidor)
        direccion_completa = os.path.join(DIRECTORIO_PREDICCIONES, archivo)
        print("Leyendo archivo " + direccion_completa)


        with open(direccion_completa, 'r') as file:

            predicciones_steps = pd.read_csv(file, header=None)
            data = predicciones_steps[0][0]
            predicciones[y][x] = float(data)

        os.remove(direccion_completa)
        
    # guardamos la matriz de predicciones
    print(f"Predicciones para step {step} listas")
    aux = ""
    if step < 10:
        aux = "0" + str(step)
    else:
        aux = str(step)

    # Guardar la matriz en un archivo CSV
    nombre_archivo = f"matriz_prediccion_step_{step}.csv"
    print(f"Guardando matriz en {nombre_archivo}")

    guardar_matriz(predicciones, DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES, nombre_archivo)

    # ahora voy a graficar un mapa de calor con las predicciones      
    nombre_imagen = f"imagen_prediccion_step_{aux}.png"
    crear_heatmap(predicciones,DIRECTORIO_IMAGENES_GENERADADS,nombre_imagen, "Prediccion Step " + str(step))


if __name__ == "__main__":
    step = int(sys.argv[1])
    armar_prediccion(step)