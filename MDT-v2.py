import os
import shutil
from urllib.request import urlopen
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import logging

# Configurar logging
logging.basicConfig(filename='mdl_downloader.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MDLDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("MDL Downloader")
        self.window.geometry("720x400")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.file_path = ctk.StringVar()
        self.status = ctk.StringVar()
        self.progress = ctk.DoubleVar()

        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Entrada de archivo
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(file_frame, text="Archivo MDL:").pack(side="left", padx=(0, 10))
        ctk.CTkEntry(file_frame, textvariable=self.file_path, width=300).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(file_frame, text="Examinar", command=self.browse_file).pack(side="right")

        # Área de información
        self.info_text = ctk.CTkTextbox(main_frame, height=150, width=460)
        self.info_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Botón de descarga
        self.download_button = ctk.CTkButton(main_frame, text="Descargar", command=self.start_download, state="disabled")
        self.download_button.pack(pady=10)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(main_frame, textvariable=self.status)
        self.status_label.pack(pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("MDL files", "*.mdl")])
        if filename:
            self.file_path.set(filename)
            self.process_file()

    def process_file(self):
        try:
            lineas = self.leer_archivo_mdl(self.file_path.get())
            cabecera = self.extraer_cabecera(lineas)
            self.mostrar_cabecera(cabecera)
            self.download_button.configure(state="normal")
        except Exception as e:
            logging.exception("Error al procesar el archivo")
            error_message = f"No se pudo procesar el archivo: {str(e)}\n\nRevisa el archivo 'mdl_downloader.log' para más detalles."
            messagebox.showerror("Error", error_message)

    def start_download(self):
        self.download_button.configure(state="disabled")
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        try:
            ruta_descarga = os.path.join(os.getcwd(), 'download')
            lineas = self.leer_archivo_mdl(self.file_path.get())
            data_lines = lineas[lineas.index("$data-start\n")+1:]
            self.descargar_archivos(data_lines, ruta_descarga)
            shutil.copy(self.file_path.get(), ruta_descarga)
            self.window.after(0, lambda: messagebox.showinfo("Éxito", "Descarga completa"))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Error", f"Error durante la descarga: {str(e)}"))
        finally:
            self.window.after(0, lambda: self.download_button.configure(state="normal"))

    def leer_archivo_mdl(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                return archivo.readlines()
        except UnicodeDecodeError:
            logging.warning("Error al decodificar con UTF-8, intentando con ISO-8859-1")
            with open(ruta_archivo, 'r', encoding='iso-8859-1') as archivo:
                return archivo.readlines()

    def corregir_errores_tipograficos(self, clave):
        correcciones = {
            'TotalArchibes': 'TotalArchives',
            'TotalArchibos': 'TotalArchives',
            'TotalArchivos': 'TotalArchives',
            'TotalSize': 'TotalSize',
            'TotalTamaño': 'TotalSize',
            'Tamaño': 'TotalSize',
            'Autor': 'Author',
            'Descripcion': 'Description',
            'Descripción': 'Description',
        }
        return correcciones.get(clave, clave)

    def extraer_cabecera(self, lineas):
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
                    clave_corregida = self.corregir_errores_tipograficos(clave)
                    valor = ': '.join(partes[1:]).rstrip(';').strip()
                    cabecera[clave_corregida] = valor
        
        logging.debug(f"Cabecera extraída: {cabecera}")
        
        # Verificar que todos los campos necesarios estén presentes
        campos_requeridos = ['Name', 'Version', 'NReg', 'TotalSize', 'TotalArchives', 'Author', 'Description']
        for campo in campos_requeridos:
            if campo not in cabecera:
                raise KeyError(f"Campo requerido '{campo}' no encontrado en la cabecera del archivo MDL")
        
        return cabecera

    def mostrar_cabecera(self, cabecera):
        info = f"Nombre del paquete: {cabecera['Name']}\n"
        info += f"Versión: {cabecera['Version']}\n"
        info += f"Número de registro: {cabecera['NReg']}\n"
        info += f"Peso total: {cabecera['TotalSize']}\n"
        info += f"Número de archivos: {cabecera['TotalArchives']}\n"
        info += f"Autor: {cabecera['Author']}\n"
        info += f"Descripción: {cabecera['Description']}\n"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)

    def descargar_archivos(self, data_lines, ruta_descarga):
        directorios = [ruta_descarga]
        total_files = sum(1 for line in data_lines if line.strip() and not line.strip().startswith(("dir", "}")))
        files_downloaded = 0

        for linea in data_lines:
            if linea.strip() == "$data-end":
                break
            elif linea.strip() == "$data-start":
                continue
            elif linea.strip().startswith("dir"):
                carpeta = linea.strip().split("[")[1].split("]")[0]
                directorios.append(carpeta)
            elif linea.strip().startswith("}"):
                directorios.pop()
            else:
                url = linea.strip()
                archivo_nombre = url.split("/")[-1]
                nueva_ruta = os.path.join(*directorios)
                if not os.path.exists(nueva_ruta):
                    os.makedirs(nueva_ruta)
                ruta_archivo = os.path.join(nueva_ruta, archivo_nombre)
                if not os.path.isdir(ruta_archivo):
                    self.descargar_archivo(url, ruta_archivo)
                    files_downloaded += 1
                    progress = files_downloaded / total_files
                    self.window.after(0, lambda p=progress: self.progress_bar.set(p))
                    self.window.after(0, lambda f=files_downloaded, t=total_files: 
                                      self.status.set(f"Descargando: {f}/{t}"))

    def descargar_archivo(self, url, ruta_archivo):
        with open(ruta_archivo, 'wb') as archivo:
            with urlopen(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    archivo.write(buffer)
                    if total_size > 0:
                        percent = downloaded / total_size
                        self.window.after(0, lambda p=percent: self.progress_bar.set(p))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MDLDownloader()
    app.run()
