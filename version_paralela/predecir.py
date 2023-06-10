import numpy as np
import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults

directorio_modelos = './modelos/'

# cargo los modelos en un dict con clave el nombre del archivo
modelos = {}
archivos_csv = [f for f in os.listdir(directorio_modelos) if f.endswith('.pkl')]
for archivo in archivos_csv:
    print('Procesando archivo: ' + archivo)
    ruta_completa = os.path.join(directorio_modelos, archivo)
    modelo = ARIMAResults.load(ruta_completa)
    modelos[archivo[:-4]] = modelo

# ahora voy a predecir el siguiente valor para cada medidor
# voy a guardar las predicciones en una matriz de 16 x 16, cada posicion es la predicion de un medidor
# y luego graficaré un mapa de calor con esa matriz
predicciones = np.zeros((16, 16))
for i in range(16):
    for j in range(16):
        numMedidor = i * 16 + j
        # obtengo el nombre del archivo
        clave = 'medidor_' + str(numMedidor)
        # obtengo el modelo
        modelo = modelos[clave]
        # hago la prediccion
        prediccion = modelo.forecast(steps=1)[0]
        # guardo la prediccion
        predicciones[i, j] = prediccion

       
# ahora voy a graficar un mapa de calor con las predicciones
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 10))
sns.heatmap(predicciones, annot=True, fmt='.1f', cmap='Blues')
plt.show()
