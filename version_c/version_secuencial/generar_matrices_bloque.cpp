#include <armadillo>
#include <boost/filesystem.hpp>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <filesystem>

#include "config.h"
using namespace std;

bool coordenada_en_mascara(int x, int y, int** mascara_cargada){
    return mascara_cargada[y][x] == 1;
}

void convertir_latlong_a_cord(float latitud, float longitud, int* ret){
    float latitud_redondeado = ceil(latitud * 100.0) / 100.0;
    float longitud_redondeado = ceil(longitud * 100.0) / 100.0;

    float lat_min = -30.33;
    float lat_max = -34.7;
    
    float long_max = -53.4;
    float long_min = -58.33;

    int y = (int)((latitud_redondeado - lat_min) / (lat_max - lat_min) * 14) + 1;
    int x = (int)((longitud_redondeado - long_min) / (long_max - long_min) * 15);

    ret[0] = x;
    ret[1] = y;
}

void convertir_medidor_a_cord(int numMedidor, int* ret){
    int y = floor(numMedidor / 16);
    int x = numMedidor % 16;
    ret[0] = x;
    ret[1] = y;
}

void generar_matrices_bloque(){
    int tamano_matriz_x = 16;
    int tamano_matriz_y = 16;

    string directorio_csvs = "";
}

int main(){
    cout << "Hello world!" << endl;
    cout << "DIRECTORIO_CSVS_DATOS: " << DIRECTORIO_CSVS_DATOS << endl;

    return 0;
}