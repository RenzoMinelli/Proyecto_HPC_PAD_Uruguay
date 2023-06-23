import numpy as np
import pandas as pd
import os
import time 
from math import floor 
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap
from config import *
from keras.models import load_model
import multiprocessing as mp

directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

# Directorio donde se guardarán las imágenes
directorio_guardado = DIRECTORIO_IMAGENES_GENERADADS

cantidad_fuera_del_medidor = 1
ancho_bloque = cantidad_fuera_del_medidor * 2 + 1
cantidadMedidores = 16*16
tamaño_matriz = TAMAÑO_MATRIZ



def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

def procesar_modelos(archivos_modelos, cola_res):
    process = mp.current_process()
    pid = process.pid

    for archivo in archivos_modelos:

        print(f"Proceso {pid} procesando {archivo}")

        ruta_completa = os.path.join(directorio_modelos, archivo)
        num_modelo = archivo[:-3]
        modelo = load_model(ruta_completa)

        ruta_completa_matriz = os.path.join(DIRECTORIO_CSVS_MATRICES_GENERADAS, num_modelo + '.csv')
        df = pd.read_csv(ruta_completa_matriz, header=None)
        matriz = df.values

        df = pd.DataFrame(matriz[-1:,:]).drop(columns=[0])
        lista = df.values
        bloque = lista.reshape(1, 9)
        # predigo
        prediccion = modelo.predict(bloque)
        prediccion = prediccion[0,0]
        cola_res.put((num_modelo, prediccion))

def predecir_por_bloque():
    steps = PASOS_PREDICCION
    archivos_modelos = [f for f in os.listdir(directorio_modelos) if f.endswith('.h5')]
    
    cantidad_modelos = len(archivos_modelos)
    cantidad_modelos_por_proceso = int(cantidad_modelos / NUMERO_DE_PROCESOS)
    
    ruta_al_archivo = DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES

    for k in range(steps):

        cola_res = mp.Queue()
        procesos = []

        for nro_proceso in range(NUMERO_DE_PROCESOS):
            primer_modelo = nro_proceso * cantidad_modelos_por_proceso
            ultimo_modelo = min(primer_modelo + cantidad_modelos_por_proceso,cantidad_modelos)
            modelos = archivos_modelos[primer_modelo:ultimo_modelo]
            procesos.append(mp.Process(target=procesar_modelos, args=(modelos, cola_res)))
        
        for proceso in procesos:
            proceso.start()

        predicciones = np.zeros(tamaño_matriz)

        for it in range(cantidad_modelos):
            num_medidor, prediccion = cola_res.get()
            x,y = convertir_medidor_a_cord(int(num_medidor))
            predicciones[y,x] = prediccion

        # Guardar la matriz en un archivo CSV
        nombre_archivo = f"matriz_prediccion_step_{k}.csv"
        guardar_matriz(predicciones, ruta_al_archivo, nombre_archivo)

        # ahora voy a graficar un mapa de calor con las predicciones      
        nombre_imagen = f"imagen_prediccion_step_{k}.png"
        crear_heatmap(predicciones,directorio_guardado,nombre_imagen, "Prediccion Step " + str(k))

        fila = np.zeros(ancho_bloque*ancho_bloque + 1)
        fila[0] = time.time()

        print("AGREGANDO NUEVA FILA A CSV")
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
                        valor = predicciones[posMatrizY_orig][posMatrizX_orig]
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
    predecir_por_bloque()
