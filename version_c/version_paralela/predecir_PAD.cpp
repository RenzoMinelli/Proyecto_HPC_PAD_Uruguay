#include <omp.h>
#include <iostream>
#include <cstdlib>
#include <vector>
#include <filesystem>
#include <string>
#include <cmath>
#include <unistd.h>
#include <chrono>
#include <thread>
#include <dirent.h>
#include <algorithm> 

using namespace std;

#define NUMERO_DE_PROCESOS 15
#define N 10 

int generar_matrices_por_bloques() {

    string DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES = "matrices_por_fecha_anteriores";
    const int num_medidores = 16*16;
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    const int mascara[16][16] = {
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
        {0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0},
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
    };

    // Generamos las matrices del mapa entero en cada instante
    string pythonScriptPath = current_working_dir + "/scripts_python/generar_matrices_mapa.py"; 

    vector<string> files;
    
    for(auto& p: filesystem::directory_iterator("datos")) {
        files.push_back(p.path().filename());
    }
    // Ordena el vector
    std::sort(files.begin(), files.end());

    int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));
   
    #pragma omp parallel for
    for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
        int firstFile = i * numFilesPerProcess;
        int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
        for(int j=firstFile; j<lastFile; j++) {
            string command = "python3 " + pythonScriptPath + " " + files[j];
            system(command.c_str());
        }
    }
    
    // ahora por cada medidor lanzamos un proceso que genere las matrices de bloque de ese medidor
    pythonScriptPath = current_working_dir + "/scripts_python/generar_matrices_bloque.py";  
    
    // obtengo la lista filtrada de medidores que si estan en la mascara
    vector<int> medidores_en_mascara;
    for(int i=0; i<16; i++) {
        for(int j=0; j<16; j++) {

            if(mascara[i][j] == 1) {
                medidores_en_mascara.push_back(i*16 + j);
            }
        }
    }
    int num_medidores_en_mascara = medidores_en_mascara.size();
    int medidores_por_proceso = ceil(num_medidores_en_mascara / static_cast<double>(NUMERO_DE_PROCESOS));

    #pragma omp parallel for
    for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
        int primerMedidor = i * medidores_por_proceso;
        int ultimoMedidor = min(primerMedidor + medidores_por_proceso, num_medidores_en_mascara);
        for(int j=primerMedidor; j<ultimoMedidor; j++) {
            string command = "python3 " + pythonScriptPath + " " + to_string(medidores_en_mascara[j]);
            system(command.c_str());
        }
    }

    return 0;
}

int generar_imagenes_fechas_anteriores(){
    // Generamos las imagenes de fechas anteriores 
   
      
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;

    string pythonScriptPath = current_working_dir + "/scripts_python/generar_imagen_de_archivo.py";  
    files.clear();

    string carpeta = "./matrices_por_fecha_anteriores/" ;
    for(auto& p: filesystem::directory_iterator("matrices_por_fecha_anteriores")) {
        files.push_back(p.path().filename());
    }
    // Ordena el vector
    std::sort(files.begin(), files.end());

    int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));

    #pragma omp parallel for
    for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
        int firstFile = i * numFilesPerProcess;
        int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
        for(int j=firstFile; j<lastFile; j++) {
            string command = "python3 " + pythonScriptPath + " " + files[j];
            system(command.c_str());
        }
    }
    return 0;
}

int entrenar_modelos_por_bloque(){
    // Generamos las imagenes de fechas anteriores 
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;

    string pythonScriptPath = current_working_dir + "/scripts_python/entrenar_modelos_por_bloque.py";  
    files.clear();

    for(auto& p: filesystem::directory_iterator("matrices_por_bloque")) {
        files.push_back(p.path().filename());
    }
    // Ordena el vector
    std::sort(files.begin(), files.end());

    int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));

    #pragma omp parallel for
    for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
        int firstFile = i * numFilesPerProcess;
        int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
        for(int j=firstFile; j<lastFile; j++) {
            string command = "python3 " + pythonScriptPath + " " + files[j];
            system(command.c_str());
        }
    }
    
    return 0;
}

int predecir_por_bloque(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;

    const int mascara[16][16] = {
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
        {0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0},
        {0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
        {0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0},
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
    };

    int steps = 20;

    for(int s=0; s<steps; s++){

        string pythonScriptPath = current_working_dir + "/scripts_python/predecir_por_bloque.py";  
        files.clear();

        for(auto& p: filesystem::directory_iterator("modelos")) {
            files.push_back(p.path().filename());
        }
        // Ordena el vector
        std::sort(files.begin(), files.end());

        int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));

        // obtengo la lista filtrada de medidores que si estan en la mascara
        vector<int> medidores_en_mascara;
        for(int i=0; i<16; i++) {
            for(int j=0; j<16; j++) {
                if(mascara[i][j] == 1) {
                    medidores_en_mascara.push_back(i*16 + j);
                }
            }
        }
        int num_medidores_en_mascara = medidores_en_mascara.size();
        int medidores_por_proceso = ceil(num_medidores_en_mascara / static_cast<double>(NUMERO_DE_PROCESOS));

        #pragma omp parallel for
        for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
            int firstFile = i * numFilesPerProcess;
            int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
            for(int j=firstFile; j<lastFile; j++) {
                string numModelo = files[j].substr(0, files[j].size() - 6);
                string command = "python3 " + pythonScriptPath + " " + files[j];
                system(command.c_str());
            }
        }

        // ahora en predicciones/ quedo un archivo por cada medidor y valor
        // llamamos a un python que los toma a todos, arma una matriz e imagen
        
        pythonScriptPath = current_working_dir + "/scripts_python/armar_prediccion.py";  
        string command = "python3 " + pythonScriptPath + " " + to_string(s);
        system(command.c_str());

        pythonScriptPath = current_working_dir + "/scripts_python/generar_filas_matriz_por_bloque.py";

        // matriz de preccion quedo en matrices_por_fecha_anteriores/matriz_prediccion_step_{s}.csv
        string matriz_prediccion_filename = "matriz_prediccion_step_" + to_string(s) + ".csv";

        #pragma omp parallel for
        for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
            int primerMedidor = i * medidores_por_proceso;
            int ultimoMedidor = min(primerMedidor + medidores_por_proceso, num_medidores_en_mascara);
            for(int j=primerMedidor; j<ultimoMedidor; j++) {
                string command = "python3 " + pythonScriptPath + " " + matriz_prediccion_filename + " " + to_string(medidores_en_mascara[j]);
                system(command.c_str());
            }
        }
    }

    return 0;
}

int producir_video(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    string pythonScriptPath = current_working_dir + "/scripts_python/producir_video.py";
    string command = "python3 " + pythonScriptPath ;
    system(command.c_str());

    return 0;

};

int preparar_ambiente(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    string pythonScriptPath = current_working_dir + "/scripts_python/preparar_ambiente.py";
    string command = "python3 " + pythonScriptPath ;
    system(command.c_str());

    return 0;
};

int main(int argc, char** argv) {
     int ret = 0;

    ret = preparar_ambiente();
    if(ret != 0) {
        return ret;
    }
    
    ret = generar_matrices_por_bloques();
    if(ret != 0) {
        return ret;
    }

    ret = generar_imagenes_fechas_anteriores();
    if(ret != 0) {
        return ret;
    }

    ret = entrenar_modelos_por_bloque();
    if(ret != 0) {
        return ret;
    }
   
    ret = predecir_por_bloque();
    if(ret != 0) {
        return ret;
    }
   
    ret = producir_video();
    if(ret != 0) {
        return ret;
    }

    return 0;
}
 