#include <omp.h>
#include <mpi.h>
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
    int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));

   

    MPI_Init(NULL,NULL);
  
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::vector<std::string> nombresArchivos;

    if (rank == 0) {
        DIR* directorio = opendir(carpeta.c_str());
        if (directorio != nullptr) {
            dirent* archivo;
            while ((archivo = readdir(directorio)) != nullptr) {
                if (archivo->d_type == DT_REG) {  // Solo archivos regulares
                    nombresArchivos.push_back(archivo->d_name);
                }
            }
            closedir(directorio);
        } else {
            std::cerr << "Error al abrir la carpeta" << std::endl;
            MPI_Abort(MPI_COMM_WORLD, 1);
            return 1;
        }
    }

    int totalArchivos = nombresArchivos.size();

    // Enviar la cantidad total de archivos a todos los procesos
    MPI_Bcast(&totalArchivos, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Calcular la porción de archivos que le toca a cada proceso
    int archivosPorProceso = totalArchivos / size;
    int archivosExtras = totalArchivos % size;

    int inicio = archivosPorProceso * rank + std::min(rank, archivosExtras);
    int fin = inicio + archivosPorProceso + (rank < archivosExtras ? 1 : 0);

    // Enviar la cantidad y posición de archivos a cada proceso
    int cantidadArchivos = fin - inicio;
    MPI_Send(&cantidadArchivos, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);
    MPI_Send(&inicio, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);

    // Cada proceso imprime su información de archivos
    std::cout << "Proceso " << rank << ": Imprimir " << cantidadArchivos << " archivos a partir de la posición " << inicio << std::endl;


    for(int j=inicio; j<inicio+cantidadArchivos; j++) {
        string command = "python3 " + pythonScriptPath + " " + files[j];
        system(command.c_str());
    }

    MPI_Finalize();



    
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

    string pythonScriptPath = current_working_dir + "/scripts_python/predecir_por_bloque.py";  
    files.clear();

    for(auto& p: filesystem::directory_iterator("modelos")) {
        files.push_back(p.path().filename());
    }
    int numFilesPerProcess = ceil(files.size() / static_cast<double>(NUMERO_DE_PROCESOS));
    int steps = 10;

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
            string command = "python3 " + pythonScriptPath + " " + files[j] + " " + to_string(steps);
            system(command.c_str());
        }
    }

    // ahora en predicciones/ quedo un archivo por cada medidor y valor
    // llamamos a un python que los toma a todos, arma una matriz e imagen

    #pragma omp parallel for
    for(int s=0; s<steps; s++){
        pythonScriptPath = current_working_dir + "/scripts_python/armar_prediccion.py";  
        string command = "python3 " + pythonScriptPath + " " + to_string(s);
        system(command.c_str());
    }
        
    return 0;
}

int producir_video(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;

    string pythonScriptPath = current_working_dir + "/scripts_python/producir_video.py";
    string command = "python3 " + pythonScriptPath ;
    system(command.c_str());

    return 0;

};


void listarArchivos() {
       
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

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::vector<std::string> nombresArchivos;

    if (rank == 0) {
        DIR* directorio = opendir(carpeta.c_str());
        if (directorio != nullptr) {
            dirent* archivo;
            while ((archivo = readdir(directorio)) != nullptr) {
                if (archivo->d_type == DT_REG) {  // Solo archivos regulares
                    nombresArchivos.push_back(archivo->d_name);
                }
            }
            closedir(directorio);
        } else {
            std::cerr << "Error al abrir la carpeta" << std::endl;
            MPI_Abort(MPI_COMM_WORLD, 1);
            return;
        }
    }

    int totalArchivos = nombresArchivos.size();

    // Enviar la cantidad total de archivos a todos los procesos
    MPI_Bcast(&totalArchivos, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Calcular la porción de archivos que le toca a cada proceso
    int archivosPorProceso = totalArchivos / size;
    int archivosExtras = totalArchivos % size;

    int inicio = archivosPorProceso * rank + std::min(rank, archivosExtras);
    int fin = inicio + archivosPorProceso + (rank < archivosExtras ? 1 : 0);

    // Enviar la cantidad y posición de archivos a cada proceso
    int cantidadArchivos = fin - inicio;
    MPI_Send(&cantidadArchivos, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);
    MPI_Send(&inicio, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);

    // Cada proceso imprime su información de archivos
    std::cout << "Proceso " << rank << ": Imprimir " << cantidadArchivos << " archivos a partir de la posición " << inicio << std::endl;



    for(int j=inicio; j<inicio+cantidadArchivos; j++) {
        string command = "python3 " + pythonScriptPath + " " + files[j];
        system(command.c_str());
    }

}

int main(int argc, char** argv) {
     int ret = 0;
    
    MPI_Init(&argc, &argv);
    listarArchivos();
    MPI_Finalize();
    


/*int main(){
   

    ret = generar_matrices_por_bloques();
    if(ret != 0) {
        return ret;
    }

    ret = generar_imagenes_fechas_anteriores();
    if(ret != 0) {
        return ret;
    }
/*
    ret = entrenar_modelos_por_bloque();
    if(ret != 0) {
        return ret;
    }
    
    ret = predecir_por_bloque();
    if(ret != 0) {
        return ret;
    }
  */ 
    ret = producir_video();
    if(ret != 0) {
        return ret;
    }

    return 0;
}
 