import cv2
import os
from config import *

def producir_video():

    # Directorio donde se encuentran las imágenes generadas
    directorio_imagenes = DIRECTORIO_IMAGENES_GENERADADS

    # Obtener la lista de archivos en el directorio
    archivos = os.listdir(directorio_imagenes)

    # Ordenar los archivos por nombre
    archivos_ordenados = sorted(archivos)

    # Definir el tamaño de las imágenes y la frecuencia de cuadros por segundo del video
    tamaño_imagen = (640, 480)
    fps = 4.0

    # Crear el objeto VideoWriter
    nombre_video = 'video_salida.mp4'
    video_salida = cv2.VideoWriter(nombre_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, tamaño_imagen)

    # Recorrer cada archivo de imagen en orden y agregarlo al video
    for archivo in archivos_ordenados:
        # Obtener la ruta completa de la imagen
        ruta_imagen = os.path.join(directorio_imagenes, archivo)
        
        # Leer la imagen utilizando OpenCV
        imagen = cv2.imread(ruta_imagen)
        
        # Escribir la imagen en el video de salida
        video_salida.write(imagen)

    # Cerrar el objeto VideoWriter y liberar los recursos
    video_salida.release()

    # Imprimir un mensaje de finalización
    print("El video se ha creado correctamente.")


if __name__ == "__main__":
    producir_video()
