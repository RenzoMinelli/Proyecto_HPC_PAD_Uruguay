import pandas as pd
import numpy as np

filas = {}
filas['fila00'] = [0]
filas['fila01'] = [0,0,1,1,1,1,1]
filas['fila02'] = [0,1,1,1,1,1,1,1]
filas['fila03'] = [0,1,1,1,1,1,1,1,1,1]
filas['fila04'] = [0,1,1,1,1,1,1,1,1,1,1,1]
filas['fila05'] = [0,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila06'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila07'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila08'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila09'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila10'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila11'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila12'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila13'] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
filas['fila14'] = [0,0,0,0,1,1,1,1,1,1,1,1,1,1]
filas['fila15'] = [0]

# completo con 0 cada fila hasta llegar a 16 elementos
for fila in filas:
    while len(filas[fila]) < 16:
        filas[fila].append(0)

# genero una matriz 16x16 y guardo un csv con la matriz de enteros
matriz = np.zeros((16,16), dtype=int)
for fila in filas:
    matriz[int(fila[-2:])]=filas[fila]
df = pd.DataFrame(matriz)
df.to_csv('auxiliar/mascara.csv', header=None, index=None)


