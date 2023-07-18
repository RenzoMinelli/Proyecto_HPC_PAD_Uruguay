import os 

file_directory = os.path.dirname(os.path.realpath(__file__)) + "/.."

DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES = f'{file_directory}/matrices_por_fecha_anteriores/'
DIRECTORIO_CSVS_DATOS = f"{file_directory}/datos/"
DIRECTORIO_CSVS_MATRICES_GENERADAS = f'{file_directory}/matrices_por_bloque/'
DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR = f'{file_directory}/matrices_por_medidor/'
DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA = f'{file_directory}/matrices_por_bloque_anteriores/'
DIRECTORIO_MODELOS_GENERADOS = f'{file_directory}/modelos/'
DIRECTORIO_IMAGENES_GENERADADS = f'{file_directory}/images/'
DIRECTORIO_AUXILIAR = f'{file_directory}/auxiliar/'
DIRECTORIO_PREDICCIONES = f'{file_directory}/predicciones/'
DIRECTORIO_TRAINING_DATA = f'{file_directory}/training_data/'
ARCHIVO_TIEMPO_SECUENCIAL = f'{file_directory}/registro_tiempo.txt'

TAMAÑO_MATRIZ = (16, 16)
NUMERO_DE_PROCESOS = 15
PASOS_PREDICCION = 20
