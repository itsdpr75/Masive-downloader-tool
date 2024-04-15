# Bienvenido a mi nuevo programa

# ¿De que se trata?

MDT o Masive Downloader Tool es una herramienta para descargar grandes cantidades de archivos sin necesidad de enviarlos comprimidos.
Este programa lee un archivo .MDL (Masive Download Link) el cual se compone de 2 partes:

    1. Cabecera:
        Esta parte es mera informacion sobre el archivo, contiene un nombre, version descripcion, informacion y un numero de registro para cualquier cosa
    2. Datos:
        Esta parte contiene las carpetas y enlaces de los archivos que se descargarán mas tarde

Los archivos MDL se pueden crear con cualquier editor de texto sin formato o editor de codigo, ya que no requiere ninguna caracteristica especial. Puedes usar el bloc de notas

# Este es un ejemplo de un archivo mdl por dentro:

La cabecera tiene que ser una lista que comienze por $info y acabe por $ofni, no excluyas nada de la lista ya que podrias probocar errores, modifica despues de los dos puntos asta el punto y coma.

Si no quieres poner alguna cosa en la cabecera pon cualquier cosa, pero no lo dejes vacio. pon un "nose" o un "xd"

$info

Name: nombre del paquete;
Version: version;
NReg: Codigo del registro;
TotalSize: suma del peso total de todos los archivos;
TotalArchibes: cantidad total de archivos en formato numero;
Author: nombre del autor;
Description: descripcion del paquete;

$ofni



$data-start

dir [carpeta1]{
    https://example.com/example.txt
	https://example.com/example.log
	https://example.com/example.html
	https://example.com/example.wav
	dir [carpeta2]{
		https://example.com/example.wmv
	}
	https://example.com/example.mp3
	dir [carpeta3]{
		https://example.com/example.wmv
	}
}

$data-end



No se si lo abras notado pero las carpetas son así:
	dir [nombre de la carpeta]{
		enlaces que se descargaran dentro de la carpeta
        y otras carpetas
	}

No elimines la primera carpeta

# En el archivo PDF tienes una mejor explicacion del uso del programa y creacion de un archivo mdl

# Proximamente are un video sobre esto
























































































































































































































































































































































































que miras bro?