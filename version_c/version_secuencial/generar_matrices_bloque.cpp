#include <armadillo>
#include <boost/filesystem.hpp>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <filesystem>

void saveMatrixAsCSV(const arma::mat& matrix, const std::string& filename)
{
    std::ofstream outputFile(filename);
    outputFile << matrix;
    outputFile.close();
}

arma::mat loadCSV(const std::string& filename)
{
    arma::mat matrix;
    matrix.load(filename, arma::csv_ascii);
    return matrix;
}

std::vector<boost::filesystem::path> listFilesInDirectory(const std::string& directoryPath, const std::string& fileExtension)
{
    std::vector<boost::filesystem::path> files;
    boost::filesystem::directory_iterator endIterator;
    for (boost::filesystem::directory_iterator file(directoryPath); file != endIterator; ++file)
    {
        if (boost::filesystem::is_regular_file(file->status()) && file->path().extension() == fileExtension)
        {
            files.push_back(file->path());
        }
    }
    return files;
}

void processMatrix(arma::mat& matrix)
{
    for (arma::uword i = 0; i < matrix.n_rows; ++i)
    {
        for (arma::uword j = 0; j < matrix.n_cols; ++j)
        {
            // Process matrix(i, j)...
        }
    }
}

bool coordenada_en_mascara(int x, int y, int** mascara_cargada){
    return mascara_cargada[y][x] == 1;
}

void convertir_latlong_a_cord(float latitud, float longitud, int* ret){
    float latitud_redondeado = ceil(latitud, 2);
    float longitud_redondeado = ceil(longitud, 2);

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
    int tamaño_matriz_x = 16;
    int tamaño_matriz_y = 16;

    string directorio_csvs = "";
}
