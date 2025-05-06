import os
import shutil
from urllib.request import urlopen
from lib.tqdm.tqdm import tqdm

def leer_archivo_mdl(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        lineas = archivo.readlines()
    return lineas

def extraer_cabecera(lineas):
    cabecera = {}
    in_cabecera = False
    for linea in lineas:
        if not in_cabecera:
            if linea.strip() == "$info":
                in_cabecera = True
            continue
        elif linea.strip() == "$ofni":
            break
        else:
            partes = linea.strip().split(': ')
            if len(partes) >= 2:
                clave = partes[0].strip()
                valor = partes[1].rstrip(';').strip()
                cabecera[clave] = valor
    return cabecera

def mostrar_cabecera(cabecera):
    print("Nombre del paquete:", cabecera['Name'])
    print("Versión:", cabecera['Version'])
    print("Número de registro:", cabecera['NReg'])
    print("Peso total:", cabecera['TotalSize'])
    print("Número de archivos:", cabecera['TotalArchives'])
    print("Autor:", cabecera['Author'])
    print("Descripción:", cabecera['Description'])

def descargar_archivos(data_lines, ruta_descarga):
    directorios = [ruta_descarga]  # Inicializar la pila de directorios con la ruta de descarga
    for linea in data_lines:
        if linea.strip() == "$data-end":
            break
        elif linea.strip() == "$data-start":
            continue
        elif linea.strip().startswith("dir"):
            # Obtener el nombre de la carpeta
            carpeta = linea.strip().split("[")[1].split("]")[0]
            directorios.append(carpeta)  # Añadir la nueva carpeta a la pila de directorios
        elif linea.strip().startswith("}"):
            # Salir del directorio actual
            directorios.pop()
        else:
            url = linea.strip()
            archivo_nombre = url.split("/")[-1]
            # Unir la lista de directorios en una ruta de archivo completa
            nueva_ruta = os.path.join(*directorios)
            if not os.path.exists(nueva_ruta):
                os.makedirs(nueva_ruta)
            ruta_archivo = os.path.join(nueva_ruta, archivo_nombre)
            if not os.path.isdir(ruta_archivo):  # Verificar si la ruta es un archivo y no un directorio
                with open(ruta_archivo, 'wb') as archivo:
                    with urlopen(url) as response:
                        total_size = response.length
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=archivo_nombre, ascii=True) as pbar:
                            while True:
                                data = response.read(1024)
                                if not data:
                                    break
                                archivo.write(data)
                                pbar.update(len(data))
                # Verificar el tamaño del archivo descargado
                if os.path.getsize(ruta_archivo) < total_size:
                    print("El archivo {} no se descargó correctamente. Reiniciando la descarga del archivo".format(archivo_nombre))
                    descargar_archivos([linea], ruta_descarga)

def main():
    ruta_archivo = input("Introduce la ruta o arrastra del archivo .mdl aquí: ")
    lineas = leer_archivo_mdl(ruta_archivo)
    cabecera = extraer_cabecera(lineas)
    mostrar_cabecera(cabecera)
    respuesta = input("¿Desea descargar el paquete {}? Se descargará un total de {} y {} archivos. Escriba S para descargar y N para cancelar: ".format(cabecera['Name'], cabecera['TotalSize'], cabecera['TotalArchives']))
    if respuesta.upper() == 'S':
        # Establecer la ruta de descarga por defecto a la carpeta "download" en el directorio actual
        ruta_descarga = os.path.join(os.getcwd(), 'download')
        data_lines = lineas[lineas.index("$data-start\n")+1:]
        descargar_archivos(data_lines, ruta_descarga)
        print("Descarga completa.")
        # Copiar el archivo .mdl a la carpeta de descarga
        shutil.copy(ruta_archivo, ruta_descarga)
    elif respuesta.upper() == 'N':
        print("Descarga cancelada.")
    else:
        print("Respuesta no válida.")

if __name__ == "__main__":
    main()
