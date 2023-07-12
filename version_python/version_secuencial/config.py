import os 

file_directory = os.path.dirname(os.path.realpath(__file__))

DIRECTORIO_CSVS_DATOS = f"{file_directory}/datos/"
DIRECTORIO_CSVS_MATRICES_GENERADAS = f'{file_directory}/matrices_por_bloque/'
DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR = f'{file_directory}/matrices_por_medidor/'
DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA = f'{file_directory}/matrices_por_bloque_anteriores/'
DIRECTORIO_MODELOS_GENERADOS = f'{file_directory}/modelos/'
DIRECTORIO_IMAGENES_GENERADADS = f'{file_directory}/images/'
DIRECTORIO_AUXILIAR = f'{file_directory}/auxiliar/'
ARCHIVO_TIEMPO_SECUENCIAL = f'{file_directory}/registro_tiempo.txt'
TAMAÑO_MATRIZ = (16, 16)
