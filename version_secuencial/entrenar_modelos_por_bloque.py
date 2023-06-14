import numpy as np
import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA
import torch
import torch.nn as nn
from LSTM import LSTM
from config import * 

ancho_bloque = 9

# Definición de la función de entrenamiento
def train_model(data, model, loss_function, optimizer, epochs):
    for i in range(epochs):
        model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                        torch.zeros(1, 1, model.hidden_layer_size))

        optimizer.zero_grad()
        y_pred = model(data)

        single_loss = loss_function(y_pred, data)
        single_loss.backward()
        optimizer.step()

        if i%25 == 1:
            print(f'epoch: {i:3} loss: {single_loss.item():10.8f}')

    print(f'epoch: {i:3} loss: {single_loss.item():10.10f}')

def save_model(model_fit, filename):
    torch.save(model_fit.state_dict(), filename)


def entrenar_modelos_por_bloque():
    directorio_matrices = DIRECTORIO_CSVS_MATRICES_GENERADAS

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
        df = pd.DataFrame(matrices[clave]).drop(columns=[0])

        lista = df.values.astype(float)
        bloque = torch.FloatTensor(lista)

        # define el modelo
        modelo = LSTM(ancho_bloque, 100, 1)
        loss_function = nn.MSELoss()  # Función de pérdida
        optimizer = torch.optim.Adam(modelo.parameters(), lr=0.001)  # Optimizador
        # entreno el modelo
        train_model(bloque, modelo, loss_function, optimizer, epochs=150)
        # guardo el modelo
        modelos[clave] = modelo

    # ahora guardo los modelos en archivos
    directorio_modelos = DIRECTORIO_MODELOS_GENERADOS

    for clave in modelos.keys():
        print('Procesando clave: ' + clave)
        # obtengo el modelo
        modelo = modelos[clave]
        # genero el nombre del archivo
        nombre_archivo = clave + '.pt'
        # guardo el modelo
        save_model(modelo, directorio_modelos + nombre_archivo)

if __name__ == "__main__":
    entrenar_modelos_por_bloque()
