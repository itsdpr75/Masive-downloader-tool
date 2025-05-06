import os
import shutil
from urllib.request import urlopen
import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging

# Configurar logging
logging.basicConfig(filename='mdl_downloader.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MDLCreator:
    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("MDL Creator")
        self.window.geometry("600x500")
        
        self.header_info = {}
        self.file_structure = []
        
        self.create_header_widgets()

    def create_header_widgets(self):
        frame = ctk.CTkFrame(self.window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        fields = ['Name', 'Version', 'NReg', 'TotalSize', 'TotalArchives', 'Author', 'Description']
        self.entries = {}

        for field in fields:
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", padx=5, pady=5)
            ctk.CTkLabel(row, text=f"{field}:").pack(side="left")
            self.entries[field] = ctk.CTkEntry(row)
            self.entries[field].pack(side="right", expand=True, fill="x")

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Cancel", command=self.window.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Continue", command=self.continue_to_file_structure).pack(side="left", padx=10)

    def continue_to_file_structure(self):
        for field, entry in self.entries.items():
            self.header_info[field] = entry.get()
        
        self.window.destroy()
        self.create_file_structure_window()

    def create_file_structure_window(self):
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("MDL File Structure")
        self.window.geometry("600x500")

        frame = ctk.CTkFrame(self.window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.url_entry = ctk.CTkEntry(frame, width=300)
        self.url_entry.pack(pady=10)

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Add URL", command=self.add_url).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Add Folder", command=self.add_folder).pack(side="left", padx=5)

        self.structure_text = ctk.CTkTextbox(frame, height=300)
        self.structure_text.pack(pady=10, fill="both", expand=True)

        ctk.CTkButton(frame, text="Save MDL", command=self.save_mdl).pack(pady=10)

    def add_url(self):
        url = self.url_entry.get()
        if url:
            self.file_structure.append(url)
            self.update_structure_display()
            self.url_entry.delete(0, 'end')

    def add_folder(self):
        folder_name = ctk.CTkInputDialog(text="Enter folder name:", title="Folder Name").get_input()
        if folder_name:
            self.file_structure.append(f"dir [{folder_name}]{{")
            self.file_structure.append("}")
            self.update_structure_display()

    def update_structure_display(self):
        self.structure_text.delete("1.0", "end")
        for item in self.file_structure:
            self.structure_text.insert("end", item + "\n")

    def save_mdl(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mdl")
        if filename:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("$info\n\n")
                for key, value in self.header_info.items():
                    file.write(f"{key}: {value};\n")
                file.write("\n$ofni\n\n")
                file.write("$data-start\n\n")
                for item in self.file_structure:
                    file.write(item + "\n")
                file.write("\n$data-end")
            ctk.CTkMessagebox(title="Success", message="MDL file saved successfully!")
            self.window.destroy()

class MDLDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("MDL Downloader")
        self.window.geometry("720x450")
        
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

        # Botón para crear MDL
        create_mdl_button = ctk.CTkButton(main_frame, text="Create MDL", command=self.open_mdl_creator)
        create_mdl_button.pack(pady=(0, 10))

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
        self.download_button = ctk.CTkButton(main_frame, text="Descargar", command=self.download, state="disabled")
        self.download_button.pack(pady=10)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(main_frame, textvariable=self.status)
        self.status_label.pack(pady=5)

    def open_mdl_creator(self):
        MDLCreator(self.window)

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
            ctk.CTkMessagebox(title="Error", message=error_message)

    def download(self):
        try:
            self.download_button.configure(state="disabled")
            ruta_descarga = os.path.join(os.getcwd(), 'download')
            lineas = self.leer_archivo_mdl(self.file_path.get())
            data_lines = lineas[lineas.index("$data-start\n")+1:]
            self.descargar_archivos(data_lines, ruta_descarga)
            shutil.copy(self.file_path.get(), ruta_descarga)
            ctk.CTkMessagebox(title="Éxito", message="Descarga completa")
        except Exception as e:
            ctk.CTkMessagebox(title="Error", message=f"Error durante la descarga: {str(e)}")
        finally:
            self.download_button.configure(state="normal")

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
                    self.progress_bar.set(progress)
                    self.status.set(f"Descargando: {files_downloaded}/{total_files}")
                    self.window.update_idletasks()

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
                        self.progress_bar.set(percent)
                        self.window.update_idletasks()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MDLDownloader()
    app.run()