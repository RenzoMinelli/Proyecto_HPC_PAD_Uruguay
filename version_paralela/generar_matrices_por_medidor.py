import pandas as pd
import numpy as np
import os
from math import floor


# latitud vertical, longitud horizontal
# dado un par de coordenadas latitud longitud, devuelve la coordenada en la matriz (x e y)
def convertir_latlong_a_cord(latitud,longitud):

    lat_max = -30.3333
    lat_min = -34.6667
    long_max = -53.3333
    long_min = -58.3333

    # queremos que x sea entero este entre 0 y 15
    # queremos que y sea entero este entre 1 y 14

    y = int((latitud - lat_min) / (lat_max - lat_min) * 14) + 1
    x = int((longitud - long_min) / (long_max - long_min) * 15) 

    return x,y

# numero de medidor va desde 0 hasta 255
# dar coordenads x e y
def convertir_medidor_a_cord(numMedidor):
    y = floor(numMedidor / 16)
    x = numMedidor % 16
    return x,y

# Define el tamaño de la matriz
tamaño_matriz = (16, 16)

# Lugar donde se encuentran tus archivos CSV
directorio_csvs = './datos/'

archivos_csv = [f for f in os.listdir(directorio_csvs) if f.endswith('.csv')]


# Una lista para almacenar todas las matrices
matrices = {}

# Leer cada archivo CSV y generar la matriz para cada instante de tiempo
for archivo in archivos_csv:

    print('Procesando archivo: ' + archivo)

    ruta_completa = os.path.join(directorio_csvs, archivo)
    df = pd.read_csv(ruta_completa)

    # los archivos se llaman inia_gras_pad2006.csv, el año son los ultimos 4 digitos
    anio = archivo[-8:-4]
    # Para cada columna del archivo CSV del formato anio_mmd, genera una matriz para ese instante
    for columna in df.columns:
       
        print('Procesando columna: ' + columna)
        # si el nombre de la columna es anio_mmd (donde mm y d son numeros, d entre 1 y 3)
        if columna.startswith(anio) and (columna.endswith('1') or columna.endswith('2') or columna.endswith('3')):

            # Genero una matriz para toda esta columna
            matriz = np.zeros(tamaño_matriz)

            # para cada fila de la columna
            for index, row in df.iterrows():
                # obtengo las coordenadas de la fila
                latitud = row['Latitud']
                longitud = row['Longitud']
                # obtengo la coordenada en la matriz
                x,y = convertir_latlong_a_cord(latitud,longitud)
                # obtengo el valor de la columna
                valor = row[columna]
                # asigno el valor a la matriz
                matriz[x,y] = valor
            
            # agrego la matriz al dict con clave el nombre de la columna
            matrices[columna] = matriz

# Ahora que tenemos las matrices en cada instante, genero un vector para cada medidor
# Para cada medidor, genero un vector con todos todos los valores que tomo ese medidor en cada instante
# ordenados por instante de tiempo

directorio_matrices_por_medidor = './matrices_por_medidor/'

matrices_por_medidor = {}

# inicializo el dict con una lista vacia para cada medidor (16 x 16 medidores)
cantidad_medidores = 16 * 16
for medidor in range(0, cantidad_medidores):
    matrices_por_medidor[medidor] = []

for matriz_instante in matrices:
    for x in range(0, 16):
        for y in range(0, 16):
            # obtengo el numero de medidor
            numMedidor = x + y * 16
            # obtengo el valor de la matriz
            valor = matrices[matriz_instante][x,y]
            # agrego el valor a la lista de valores del medidor
            matrices_por_medidor[numMedidor].append(valor)

# Guardo los vectores en un archivo CSV
for medidor in matrices_por_medidor:
    # convierto la lista a un dataframe
    df = pd.DataFrame(matrices_por_medidor[medidor])
    # genero el nombre del archivo
    nombre_archivo = 'medidor_' + str(medidor) + '.csv'
    # guardo el archivo
    df.to_csv(os.path.join(directorio_matrices_por_medidor, nombre_archivo), index=False, header=False)
    