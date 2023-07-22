all: predecir_PAD predecir_PAD_MPI

predecir_PAD:
	mpic++ -fopenmp -std=c++17 predecir_PAD.cpp -o predecir_PAD

predecir_PAD_MPI:
	mpic++ -fopenmp -std=c++17 predecir_PAD_MPI.cpp -o predecir_PAD_MPI

clean:
	rm -f predecir_PAD predecir_PAD_MPI
