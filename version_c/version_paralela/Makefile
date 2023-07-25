all: predecir_PAD_MPI evaluar_predicciones

predecir_PAD_MPI:
	mpic++ -fopenmp -std=c++17 predecir_PAD_MPI.cpp -o predecir_PAD_MPI

evaluar_predicciones:
	mpic++ -fopenmp -std=c++17 evaluar_predicciones.cpp -o evaluar_predicciones

clean:
	rm -f predecir_PAD_MPI evaluar_predicciones
