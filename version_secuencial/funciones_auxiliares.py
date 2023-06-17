import csv
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os


def guardar_matriz_como_csv(matriz, ruta, nombre_archivo):
    with open(ruta+nombre_archivo, "w", newline="") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        for fila in matriz:
            escritor_csv.writerow(fila)

def crear_heatmap_de_csv(matriz,ruta,nombre_imagen):
    fig, ax = plt.subplots()
    sns.heatmap(matriz,  annot=True,fmt='.1f', cmap='coolwarm', ax=ax ,alpha=0.5)
    imagen2 = Image.open("./version_secuencial/auxiliar/Mapa_uruguay.jpg")
    imagen2 = np.array(imagen2)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    ax.imshow(imagen2, extent=[xmin, xmax, ymin, ymax], alpha=0.5)
    
    #nombre_imagen = f"imagen_{k}.png"

    ruta_guardado = os.path.join(ruta, nombre_imagen)
    plt.savefig(ruta_guardado)

    plt.close()