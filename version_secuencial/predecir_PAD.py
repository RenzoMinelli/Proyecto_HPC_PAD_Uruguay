import generar_matrices_bloque as generar
import entrenar_modelos_por_bloque as entrenar
import predecir_por_bloque as predecir 
import producir_video as producir



if __name__ == "__main__":
    
   generar.generar_matrices_bloque()
   entrenar.entrenar_modelos_por_bloque()
   predecir.predecir_por_bloque()
   producir.producir_video()
