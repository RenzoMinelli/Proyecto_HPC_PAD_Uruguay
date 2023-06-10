import pandas as pd
import numpy as np
import os

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

# Define el tamaño de la matriz
tamaño_matriz = (16, 16)

# Lugar donde se encuentran tus archivos CSV
directorio_csvs = './datos/'
directorio_matrices_por_instante = './matrices_por_instante/'
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

# Genero un archivo csv para cada matriz con el nombre la clave
for clave in matrices.keys():
    print('Generando archivo: ' + clave)
    ruta_completa = os.path.join(directorio_matrices_por_instante, clave + '.csv')
    pd.DataFrame(matrices[clave]).to_csv(ruta_completa, header=None, index=None)


# aplicacion de mascara y todo eso 
# . . . 


