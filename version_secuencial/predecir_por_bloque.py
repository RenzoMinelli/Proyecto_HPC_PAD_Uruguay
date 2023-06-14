import numpy as np
import pandas as pd
import os
from LSTM import LSTM
import torch
import matplotlib.pyplot as plt
import seaborn as sns

directorio_modelos = './modelos/'
ancho_bloque = 9

def predecir_por_bloque():
    # cargo los modelos en un dict con clave el nombre del archivo
    modelos = {}
    archivos_csv = [f for f in os.listdir(directorio_modelos) if f.endswith('.pt')]
    for archivo in archivos_csv:
        print('Procesando modelo nombre: ' + archivo)
        ruta_completa = os.path.join(directorio_modelos, archivo)

        modelo = LSTM(ancho_bloque, 100, 1)
        modelo.load_state_dict(torch.load(ruta_completa))
        modelo.eval()

        modelos[archivo[:-3]] = modelo

    print("modelos cargados: ", modelos.keys())
    # ahora voy a predecir el siguiente valor para cada medidor
    # voy a guardar las predicciones en una matriz de 16 x 16, cada posicion es la predicion de un medidor
    # y luego graficaré un mapa de calor con esa matriz

    # cargo los matrices por medidor
    directorio_matrices = './matrices_por_bloque/'
    archivos_csv = [f for f in os.listdir(directorio_matrices) if f.endswith('.csv')]
    matrices = {}
    for archivo in archivos_csv:
        print('Procesando archivo: ' + archivo)
        ruta_completa = os.path.join(directorio_matrices, archivo)
        df = pd.read_csv(ruta_completa, header=None)
        matrices[archivo[:-4]] = df.values

    predicciones = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            numMedidor = i * 16 + j 
            # obtengo el nombre del archivo
            clave = str(numMedidor)
            # obtengo el modelo
            print("clave: ", clave)
            modelo = modelos[clave]
            # hago la prediccion con las ultimas 12 filas de la matriz
            df = pd.DataFrame(matrices[clave][:,-12:]).drop(columns=[0])
            lista = df.values.astype(float)
            bloque = torch.FloatTensor(lista)

            # predigo
            prediccion = modelo(bloque)
            # guardo la prediccion
            predicciones[i, j] = prediccion.item()

        
    # ahora voy a graficar un mapa de calor con las predicciones
    plt.figure(figsize=(10, 10))
    sns.heatmap(predicciones, annot=True, fmt='.1f', cmap='Blues')
    plt.show()

if __name__ == "__main__":
    predecir_por_bloque()
