import pandas as pd
import sys

from config import *
from funciones_auxiliares import guardar_matriz_como_csv as guardar_matriz
from funciones_auxiliares import crear_heatmap_de_csv as crear_heatmap

def generar_imagenes_de_archivos(archivo):

    archivos_csv = archivo
    titulo = archivo[:-4]
    # ahora voy a graficar un mapa de calor con las predicciones      
    nombre_imagen = f"imagen_{titulo}.png"

    df = pd.read_csv(DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES+archivos_csv, header=None)
    crear_heatmap(df,DIRECTORIO_IMAGENES_GENERADADS,nombre_imagen,titulo)
    print("generada imagen " , archivos_csv)

if __name__ == "__main__":
    nombre_archivo = sys.argv[1]
    generar_imagenes_de_archivos(nombre_archivo)
