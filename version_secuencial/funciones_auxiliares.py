import csv
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from config import *


def guardar_matriz_como_csv(matriz, ruta, nombre_archivo):
    ruta_completa = os.path.join(ruta, nombre_archivo) 
    df = pd.DataFrame(matriz)
    df.to_csv(ruta_completa, header=None, index=None)

def crear_heatmap_de_csv(matriz,ruta,nombre_imagen):
    fig, ax = plt.subplots()
    sns.heatmap(matriz, cmap='coolwarm',ax=ax ,alpha=0.5)
    imagen2 = Image.open("./version_secuencial/auxiliar/Mapa_uruguay.jpg")
    imagen2 = np.array(imagen2)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    ax.imshow(imagen2, extent=[xmin, xmax, ymin, ymax], alpha=0.5)
    
    #nombre_imagen = f"imagen_{k}.png"

    ruta_guardado = os.path.join(ruta, nombre_imagen)
    plt.savefig(ruta_guardado)

    plt.close()

def iniciar_ambiente():
     # para cada constante en config.py llamada DIRECTORIO_XXX, crear un directorio con ese nombre
    print("Creando directorios...")
    for constante in dir():
        if constante.startswith("DIRECTORIO_"):
            os.makedirs(globals()[constante], exist_ok=True)

    print("Limpiando registro de tiempo de ejecucion")
    archivo = ARCHIVO_TIEMPO_SECUENCIAL  # Ruta y nombre del archivo a verificar y borrar si existe

    if os.path.exists(archivo):
        os.remove(archivo)


