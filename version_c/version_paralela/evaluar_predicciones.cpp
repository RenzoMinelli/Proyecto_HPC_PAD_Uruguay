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



int generar_matrices_por_bloques(int rank, int size, int steps_para_evaluacion) { // Pronto MPI

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
    pythonScriptPath = current_working_dir + "/scripts_python/generar_matrices_bloque_evaluacion.py";  
    
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
        string command = "python3 " + pythonScriptPath + " " + to_string(medidores_en_mascara[j]) + " " + to_string(steps_para_evaluacion);
        system(command.c_str());
    }
    

    return 0;
}

int generar_imagenes_fechas_anteriores(int rank, int size){ // Pronto MPI
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

int entrenar_modelos_por_bloque(int rank, int size, int steps_a_evaluar, int epochs){ // Pronto MPI


    // Generamos las imagenes de fechas anteriores 
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);
    vector<string> files;

    string pythonScriptPath = current_working_dir + "/scripts_python/entrenar_modelos_por_bloque_evaluacion.py";  
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
        string command = "python3 " + pythonScriptPath + " " + files[j] + " " + to_string(steps_a_evaluar)+ " " + to_string(epochs);
        system(command.c_str());
    }
    
    
    return 0;
}

int predecir_por_bloque(int rank, int size, int steps){ // Pronto MPI
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
        
        MPI_Barrier(MPI_COMM_WORLD);

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

int evaluar_predicciones(int steps_a_evaluar){
    
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    string current_working_dir(cwd);

    string pythonScriptPath = current_working_dir + "/scripts_python/evaluar_predicciones.py" + " " + to_string(steps_a_evaluar);
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
    
    int steps_a_evaluar = 5;
    if(argc > 1){ // se manda el valor de steps a predecir
        steps_a_evaluar = atoi(argv[1]);
    }
    int epochs = 5;
    if(argc > 2){ // se manda el valor de epochs
        epochs = atoi(argv[2]);
    }

    int ret,rank,size ;
    int N = 4;
    std::chrono::time_point<std::chrono::high_resolution_clock> start, end;
    std::chrono::duration<double> elapsed;

    auto now = std::chrono::system_clock::now();
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    std::tm* now_tm = std::localtime(&now_time_t);
    std::stringstream ss;
    ss << std::put_time(now_tm, "%Y_%m_%d_%H_%M_%S");

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::string nombre_archivo = "registro_tiempo_NP_" + to_string(size) + "_" + "EPOCHS_" + to_string(epochs) + "_" + ss.str() + ".txt";
    
    // instalar requerimientos
    string command = "python3 -m pip install -r requirements.txt" ;
    system(command.c_str());

    if(rank==0) {

        printf("\nSe van a evaluar %d steps\n", steps_a_evaluar);

        ret = preparar_ambiente();
        if(ret != 0) {
            return ret;
        }

        start = std::chrono::high_resolution_clock::now();
    }
    MPI_Barrier(MPI_COMM_WORLD);

    ret = generar_matrices_por_bloques(rank, size, steps_a_evaluar);
    if(ret != 0) {
        return ret;
    }
    
    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file(nombre_archivo, std::ios_base::app);
        file << "Tiempo de generar_matrices_por_bloques: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = generar_imagenes_fechas_anteriores(rank, size);
    if(ret != 0) {
        return ret;
    }

    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file(nombre_archivo, std::ios_base::app);
        file << "Tiempo de generar_imagenes_fechas_anteriores: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = entrenar_modelos_por_bloque(rank, size, steps_a_evaluar, epochs);
    if(ret != 0) {
        return ret;
    }
    
    MPI_Barrier(MPI_COMM_WORLD);

    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file(nombre_archivo, std::ios_base::app);
        file << "Tiempo de entrenar_modelos_por_bloque: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    ret = predecir_por_bloque(rank, size, steps_a_evaluar);
    if(ret != 0) {
        return ret;
    }

    MPI_Barrier(MPI_COMM_WORLD);
    
    if(rank==0) {
        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file(nombre_archivo, std::ios_base::app);
        file << "Tiempo de predecir_por_bloque: " << elapsed.count() << "s\n";
        start = std::chrono::high_resolution_clock::now();  // Reinicia el contador de tiempo para la próxima sección
    }

    MPI_Barrier(MPI_COMM_WORLD);
    
    if(rank==0)
    {
        ret = evaluar_predicciones(steps_a_evaluar, epochs);
        if(ret != 0) {
            return ret;
        }

        end = std::chrono::high_resolution_clock::now();
        elapsed = end - start;
        std::ofstream file(nombre_archivo, std::ios_base::app);
        file << "Tiempo de evaluar_predicciones: " << elapsed.count() << "s\n";
    }

    MPI_Finalize();
    return 0;
    
}
 