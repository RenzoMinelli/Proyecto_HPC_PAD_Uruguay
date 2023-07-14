#include <omp.h>
#include <iostream>
#include <cstdlib>
#include <vector>
#include <filesystem>
#include <string>
#include <cmath>
#include <unistd.h>

using namespace std;

int main() {

    const int NUMERO_DE_PROCESOS = 15;
    string DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES = "matrices_por_fecha_anteriores";
    const int num_medidores = 16*16;

    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    // Generamos las matrices del mapa entero en cada instante
    string pythonScriptPath = current_working_dir + "/scripts_python/generar_matrices_mapa.py"; 

    vector<string> files;
    
    for(auto& p: filesystem::directory_iterator("datos")) {
        files.push_back(p.path().filename());
    }
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
    int medidores_por_proceso = ceil(num_medidores / static_cast<double>(NUMERO_DE_PROCESOS));

    #pragma omp parallel for
    for(int i=0; i<NUMERO_DE_PROCESOS; i++) {
        int primerMedidor = i * medidores_por_proceso;
        int ultimoMedidor = min(primerMedidor + medidores_por_proceso, num_medidores);
        for(int j=primerMedidor; j<ultimoMedidor; j++) {
            string command = "python3 " + pythonScriptPath + " " + to_string(j);
            system(command.c_str());
        }
    }

    // Generamos las imagenes de fechas anteriores 
    pythonScriptPath = current_working_dir + "/scripts_python/generar_imagen_de_archivo.py";  
    files.clear();

    for(auto& p: filesystem::directory_iterator("matrices_por_fecha_anteriores")) {
        files.push_back(p.path().filename());
    }
    numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));

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
