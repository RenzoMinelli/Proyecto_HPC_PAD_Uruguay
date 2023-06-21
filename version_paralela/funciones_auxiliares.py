import csv
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from config import *
import config

def guardar_matriz_como_csv(matriz, ruta, nombre_archivo):
    ruta_completa = os.path.join(ruta, nombre_archivo) 
    df = pd.DataFrame(matriz)
    df.to_csv(ruta_completa, header=None, index=None)

def crear_heatmap_de_csv(matriz,ruta,nombre_imagen, titulo=""):
    fig, ax = plt.subplots()
    sns.heatmap(matriz, cmap='coolwarm',ax=ax ,alpha=0.5, vmin=0, vmax=0.4)
    imagen2 = Image.open(f"{DIRECTORIO_AUXILIAR}Mapa_uruguay.jpg")
    imagen2 = np.array(imagen2)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    ax.set_title(titulo)
    ax.imshow(imagen2, extent=[xmin, xmax, ymin, ymax], alpha=0.5)

    ruta_guardado = os.path.join(ruta, nombre_imagen)
    plt.savefig(ruta_guardado)

    plt.close()

def iniciar_ambiente():
    # para cada constante en config.py llamada DIRECTORIO_XXX, crear un directorio con ese nombre
    print("Creando directorios...")

    constantes = dir(config)
    for constante in constantes:
        if constante.startswith("DIRECTORIO_"):
            directorio = getattr(config, constante)
            os.makedirs(directorio, exist_ok=True)

            # Vaciar todas las carpetas recién generadas excepto DIRECTORIO_CSVS_DATOS y DIRECTORIO_AUXILIAR
            if constante != "DIRECTORIO_CSVS_DATOS" and constante != "DIRECTORIO_AUXILIAR":
                for archivo in os.listdir(directorio):
                    ruta_archivo = os.path.join(directorio, archivo)
                    if os.path.isfile(ruta_archivo):  # Asegurarse de que es un archivo, no un subdirectorio
                        os.remove(ruta_archivo)

    print("Limpiando registro de tiempo de ejecución")
    archivo = config.ARCHIVO_TIEMPO_SECUENCIAL  # Ruta y nombre del archivo a verificar y borrar si existe

    if os.path.exists(archivo):
        os.remove(archivo)