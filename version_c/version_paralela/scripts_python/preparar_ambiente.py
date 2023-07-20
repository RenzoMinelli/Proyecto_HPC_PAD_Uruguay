import os
from config import *
import config

def iniciar_ambiente():
    # para cada constante en config.py llamada DIRECTORIO_XXX, crear un directorio con ese nombre
    print("Creando directorios...")

    constantes = dir(config)
    for constante in constantes:
        if constante.startswith("DIRECTORIO_"):
            directorio = getattr(config, constante)
            os.makedirs(directorio, exist_ok=True)

            # Vaciar todas las carpetas recién generadas excepto DIRECTORIO_CSVS_DATOS y DIRECTORIO_AUXILIAR
            if constante != "DIRECTORIO_CSVS_DATOS" and constante != "DIRECTORIO_AUXILIAR":
                for archivo in os.listdir(directorio):
                    ruta_archivo = os.path.join(directorio, archivo)
                    if os.path.isfile(ruta_archivo):  # Asegurarse de que es un archivo, no un subdirectorio
                        os.remove(ruta_archivo)

    print("Limpiando registro de tiempo de ejecución")
    archivo = config.ARCHIVO_TIEMPO_SECUENCIAL  # Ruta y nombre del archivo a verificar y borrar si existe

    if os.path.exists(archivo):
        os.remove(archivo)

if __name__ == "__main__":
    iniciar_ambiente()
