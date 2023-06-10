import numpy as np
import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA

def train_model(data):
    model = ARIMA(data, order=(5,1,0)) # Los parámetros dependen del análisis de tus datos
    model_fit = model.fit()
    return model_fit

def save_model(model_fit, filename):
    model_fit.save(filename)


directorio_matrices = './matrices_por_medidor/'

# cargo todas las matrices en un dict con clave el nombre del archivo
matrices = {}
archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
for archivo in archivos_csv:
    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(directorio_matrices, archivo)
    df = pd.read_csv(ruta_completa, header=None)
    matrices[archivo[:-4]] = df.values

# ahora quiero entrenar un modelo para cada bloque
# voy a guardar los modelos en un dict con clave el nombre del archivo
modelos = {}
for clave in matrices.keys():
    print('Procesando clave: ' + clave)
    # obtengo la matriz
    matriz_original = matrices[clave]
    # obtengo el bloque
    bloque = matriz_original[:, :]
    # entreno el modelo
    modelo = train_model(bloque)
    # guardo el modelo
    modelos[clave] = modelo

# ahora guardo los modelos en archivos
directorio_modelos = './modelos/'

for clave in modelos.keys():
    print('Procesando clave: ' + clave)
    # obtengo el modelo
    modelo = modelos[clave]
    # genero el nombre del archivo
    nombre_archivo = clave + '.pkl'
    # guardo el modelo
    save_model(modelo, directorio_modelos + nombre_archivo)

