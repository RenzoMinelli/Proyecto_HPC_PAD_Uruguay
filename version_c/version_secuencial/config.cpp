#include "config.h"
#include <unistd.h>

char tmp[256];

const std::string file_directory = getcwd(tmp, 256);

const std::string DIRECTORIO_CSVS_DATOS = file_directory + "/datos/";
const std::string DIRECTORIO_CSVS_MATRICES_GENERADAS = file_directory + "/matrices_por_bloque/";
const std::string DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR = file_directory + "/matrices_por_medidor/";
const std::string DIRECTORIO_CSVS_MATRICES_POR_MEDIDOR_PRUEBA = file_directory + "/matrices_por_bloque_anteriores/";
const std::string DIRECTORIO_MODELOS_GENERADOS = file_directory + "/modelos/";
const std::string DIRECTORIO_IMAGENES_GENERADADS = file_directory + "/images/";
const std::string DIRECTORIO_AUXILIAR = file_directory + "/auxiliar/";
const std::string ARCHIVO_TIEMPO_SECUENCIAL = file_directory + "/registro_tiempo.txt";

const int TAMANO_MATRIZ_X = 16;
const int TAMANO_MATRIZ_Y = 16;
