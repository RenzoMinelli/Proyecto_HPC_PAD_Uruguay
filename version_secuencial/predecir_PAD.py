import time

import generar_matrices_bloque as generar
import entrenar_modelos_por_bloque as entrenar
import predecir_por_bloque as predecir 
import producir_video as producir
import os
from config import *


def registrar_tiempo(nombre_funcion, tiempo):
    with open(ARCHIVO_TIEMPO_SECUENCIAL, "a") as archivo:
        archivo.write(f"{nombre_funcion}: {tiempo} segundos\n")

def ejecutar_y_registrar(funcion):
    inicio = time.time()
    funcion()
    fin = time.time()
    tiempo_ejecucion = fin - inicio
    registrar_tiempo(funcion.__name__, tiempo_ejecucion)


if __name__ == "__main__":

    # para cada constante en config.py llamada DIRECTORIO_XXX, crear un directorio con ese nombre
    print("Creando directorios...")
    for constante in dir():
        if constante.startswith("DIRECTORIO_"):
            os.makedirs(globals()[constante], exist_ok=True)
    print("Iniciando generar matrices")
    ejecutar_y_registrar(generar.generar_matrices_bloque)
    print("Iniciando entrenar modelos")
    ejecutar_y_registrar(entrenar.entrenar_modelos_por_bloque)
    print("Iniciando predeciccion")
    ejecutar_y_registrar(predecir.predecir_por_bloque)
    print("Iniciando producir video")
    ejecutar_y_registrar(producir.producir_video)

   
  
  
  