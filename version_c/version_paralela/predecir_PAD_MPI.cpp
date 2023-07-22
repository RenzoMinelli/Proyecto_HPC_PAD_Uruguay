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
#include <algorithm>
#include <fstream>

using namespace std;

#define NUMERO_DE_PROCESOS 15 
#define NEG 4  



int generar_matrices_por_bloques() { // Pronto MPI

    string DIRECTORIO_CSVS_MATRICES_POR_FECHA_ANTERIORES = "matrices_por_fecha_anteriores";
    const int num_medidores = 16*16;
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

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

    int numFilesPerProcess = ceil(files.size() / static_cast<double>(size));
   

    int i = rank ;
    int firstFile = i * numFilesPerProcess;
    int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
    for(int j=firstFile; j<lastFile; j++) {
        string command = "python3 " + pythonScriptPath + " " + files[j];
        system(command.c_str());
    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    

   
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
    int medidores_por_proceso = ceil(num_medidores_en_mascara / static_cast<double>(size));



    int primerMedidor = i * medidores_por_proceso;
    int ultimoMedidor = min(primerMedidor + medidores_por_proceso, num_medidores_en_mascara);
    for(int j=primerMedidor; j<ultimoMedidor; j++) {
        string command = "python3 " + pythonScriptPath + " " + to_string(medidores_en_mascara[j]);
        system(command.c_str());
    }
    

    return 0;
}

int generar_imagenes_fechas_anteriores(){ // Pronto MPI
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

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int totalArchivos = files.size();

    // Enviar la cantidad total de archivos a todos los procesos
    //MPI_Bcast(&totalArchivos, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Calcular la porción de archivos que le toca a cada proceso
    int archivosPorProceso = totalArchivos / size;
    int archivosExtras = totalArchivos % size;

    int inicio = archivosPorProceso * rank + std::min(rank, archivosExtras);
    int fin = inicio + archivosPorProceso + (rank < archivosExtras ? 1 : 0);

    // Enviar la cantidad y posición de archivos a cada proceso
    int cantidadArchivos = fin - inicio;
    //MPI_Send(&cantidadArchivos, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);
    //MPI_Send(&inicio, 1, MPI_INT, rank, 0, MPI_COMM_WORLD);

    // Cada proceso imprime su información de archivos
    //std::cout << "Proceso " << rank << ": Imprimir " << cantidadArchivos << " archivos a partir de la posición " << inicio << std::endl;



    for(int j=inicio; j<inicio+cantidadArchivos; j++) {
        string command = "python3 " + pythonScriptPath + " " + files[j];
        system(command.c_str());
    }

    return 0;
}

int entrenar_modelos_por_bloque(){ // Pronto MPI

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

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

    int numFilesPerProcess = ceil(files.size() / static_cast<double>(size));

    

    int i =rank;
    int firstFile = i * numFilesPerProcess;
    int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
    for(int j=firstFile; j<lastFile; j++) {
        string command = "python3 " + pythonScriptPath + " " + files[j];
        system(command.c_str());
    }
    
    
    return 0;
}

int predecir_por_bloque(){ // Pronto MPI
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;


    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

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

    int steps = 5;

    for(int s=0; s<steps; s++){

        string pythonScriptPath = current_working_dir + "/scripts_python/predecir_por_bloque.py";  
        files.clear();

        for(auto& p: filesystem::directory_iterator("modelos")) {
            files.push_back(p.path().filename());
        }
        // Ordena el vector
        std::sort(files.begin(), files.end());

        int numFilesPerProcess = ceil(files.size() / static_cast<double>(size));

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
        int medidores_por_proceso = ceil(num_medidores_en_mascara / static_cast<double>(size));

        
        int i = rank ;
        int firstFile = i * numFilesPerProcess;
        int lastFile = min(firstFile + numFilesPerProcess, static_cast<int>(files.size()));
        for(int j=firstFile; j<lastFile; j++) {
            string numModelo = files[j].substr(0, files[j].size() - 6);
            string command = "python3 " + pythonScriptPath + " " + files[j];
            system(command.c_str());
        }
        

        
        if(rank==0){
            // ahora en predicciones/ quedo un archivo por cada medidor y valor
            // llamamos a un python que los toma a todos, arma una matriz e imagen
            
            pythonScriptPath = current_working_dir + "/scripts_python/armar_prediccion.py";  
            string command = "python3 " + pythonScriptPath + " " + to_string(s);
            system(command.c_str());
        }

         MPI_Barrier(MPI_COMM_WORLD);

        pythonScriptPath = current_working_dir + "/scripts_python/generar_filas_matriz_por_bloque.py";

        // matriz de preccion quedo en matrices_por_fecha_anteriores/matriz_prediccion_step_{s}.csv
        string matriz_prediccion_filename = "matriz_prediccion_step_" + to_string(s) + ".csv";



        int primerMedidor = i * medidores_por_proceso;
        int ultimoMedidor = min(primerMedidor + medidores_por_proceso, num_medidores_en_mascara);
        for(int j=primerMedidor; j<ultimoMedidor; j++) {
            string command = "python3 " + pythonScriptPath + " " + matriz_prediccion_filename + " " + to_string(medidores_en_mascara[j]);
            system(command.c_str());
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


void imprimir_listas(std::vector<std::vector<std::string>> listas){
    // Mostrar los nombres de archivos en cada lista
    int N = listas.size();
    for (int i = 0; i < N; ++i) {
        std::cout << "Lista " << i + 1 << ": ";
        for (const std::string& nombre : listas[i]) {
            std::cout << nombre << " ";
        }
        std::cout << std::endl;
    }
}

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
    
    int ret,rank,size ;
    int N = 4;
    std::chrono::time_point<std::chrono::high_resolution_clock> start, end;
    std::chrono::duration<double> elapsed;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if(rank==0) {
        ret = preparar_ambiente();
        if(ret != 0) {
            return ret;
        }

        start = std::chrono::high_resolution_clock::now();
    }

    ret = generar_matrices_por_bloques();
    if(ret != 0) {
        return ret;
    }
    
    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file("registro_tiempo.txt", std::ios_base::app);
        file << "Tiempo de generar_matrices_por_bloques: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = generar_imagenes_fechas_anteriores();
    if(ret != 0) {
        return ret;
    }

    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file("registro_tiempo.txt", std::ios_base::app);
        file << "Tiempo de generar_imagenes_fechas_anteriores: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = entrenar_modelos_por_bloque();
    if(ret != 0) {
        return ret;
    }
    
    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file("registro_tiempo.txt", std::ios_base::app);
        file << "Tiempo de entrenar_modelos_por_bloque: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = predecir_por_bloque();
    if(ret != 0) {
        return ret;
    }

    MPI_Barrier(MPI_COMM_WORLD);
    
    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file("registro_tiempo.txt", std::ios_base::app);
        file << "Tiempo de predecir_por_bloque: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    if(rank==0)
    {
        ret = producir_video();
        if(ret != 0) {
            return ret;
        }

        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file("registro_tiempo.txt", std::ios_base::app);
        file << "Tiempo de producir_video: " << elapsed.count() << "s\n";
    }

    MPI_Finalize();
    return 0;
    
}
 