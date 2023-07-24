
#!/usr/bin/env python3

import subprocess
import os

def is_pingable(host):
    """
    Función que verifica si se puede hacer ping a un host.
    Retorna True si el ping fue exitoso, False en caso contrario.
    """
    try:
        print(host)
        result = subprocess.run(["ping", "-c", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.returncode)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def main():
    # Lista de strings con números entre 20 y 160
    strings = []
    inicio = 'pcunix'
    fin = '.fing.edu.uy.'
    for  i in range(16,145):
       string = inicio + str(i) +fin
       strings.append(string)


    # Filtrar aquellos a los que se pueda hacer ping
    pingable_hosts = [host for host in strings if is_pingable(host)]

    # Escribir los hosts pingables en un documento de texto
    with open("hosts_pingables.txt", "w") as file:
        for host in pingable_hosts:
            print(host)
            file.write(host + "\n")

if __name__ == "__main__":
    main()
