import csv
import numpy as np
from funciones_auxiliares import guardar_matriz_como_csv,crear_heatmap_de_csv




def bilinear_interpolation(x, y, points):
    
    x1, y1 = int(x), int(y)
    x0, y0 = x1 - 1, y1 - 1
    x2, y2 = x1 + 1, y1 + 1
    q00, q01,q10, q11, q12, q21, q22 =points[x0][y0],points[x0][y1],points[x1][y0], points[x1][y1], points[x1][y2], points[x2][y1], points[x2][y2]

    if np.isnan(q00) or np.isnan(q01) or np.isnan(q10) or np.isnan(q11) or np.isnan(q12) or np.isnan(q21) or np.isnan(q22):
        valid_values = [value for value in [q00, q01, q10, q11, q12, q21, q22] if not np.isnan(value)]
        if len(valid_values) > 0:
            return np.mean(valid_values)
        else:
            return np.nan
    else:
        valid_values = [value for value in [q00, q01, q10, q11, q12, q21, q22] if not np.isnan(value)]
        return np.mean(valid_values)
    #return q11 * (x2 - x) * (y2 - y) + q21 * (x - x1) * (y2 - y) + \
    #       q12 * (x2 - x) * (y - y1) + q22 * (x - x1) * (y - y1)

def interpolate_matrix(matrix):
    original_shape = matrix.shape
    new_shape = (original_shape[0] * 2 - 1, original_shape[1] * 2 - 1)
    interpolated_matrix = np.empty(new_shape)

    interpolated_matrix[::2, ::2] = matrix
    par = 2
    for i in range(1, new_shape[0], 1):
        if par == 1 :
            par = 2
        else:
            par = 1
        for j in range(1, new_shape[1], par):
            x, y = i, j
            x_lower = (x - 1) // 2
            x_upper = x_lower + 1
            y_lower = (y - 1) // 2
            y_upper = y_lower + 1

            interpolated_value = bilinear_interpolation((x - 1) / 2, (y - 1) / 2, matrix)
            interpolated_matrix[i, j] = interpolated_value

    return interpolated_matrix

def read_matrix_from_csv(filename):
    matrix = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            matrix.append([float(value) if value != '' else np.nan for value in row])

    return np.array(matrix)

def write_matrix_to_csv(filename, matrix):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(matrix)

        
if __name__ == "__main__":
    input_file = './version_paralela/matrices_por_fecha_anteriores/2000_011.csv'
    output_file = './version_paralela/VALORES_PRUEBA/2000_011INTERPOL.csv'

    input_matrix = read_matrix_from_csv(input_file)
    crear_heatmap_de_csv(input_matrix,'./version_paralela/VALORES_PRUEBA/',"ORIGINAL.png")
    interpolated_matrix = interpolate_matrix(input_matrix)
    interpolated_matrix = interpolate_matrix(interpolated_matrix)
    interpolated_matrix = interpolate_matrix(interpolated_matrix)
    write_matrix_to_csv(output_file, interpolated_matrix)
    crear_heatmap_de_csv(interpolated_matrix,'./version_paralela/VALORES_PRUEBA/',"INTERPOL.png")
