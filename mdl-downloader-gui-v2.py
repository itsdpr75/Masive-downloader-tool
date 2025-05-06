import os
import shutil
from urllib.request import urlopen
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class MDLDownloader:
    def __init__(self, master):
        self.master = master
        master.title("MDL Downloader")
        master.geometry("500x400")

        self.file_path = tk.StringVar()
        self.status = tk.StringVar()
        self.progress = tk.DoubleVar()

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Entrada de archivo
        ttk.Label(main_frame, text="Archivo MDL:").grid(column=0, row=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.file_path, width=50).grid(column=1, row=0, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Examinar", command=self.browse_file).grid(column=2, row=0, sticky=tk.W)

        # Área de información
        self.info_text = tk.Text(main_frame, height=10, width=60, state='disabled')
        self.info_text.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))

        # Botón de descarga
        self.download_button = ttk.Button(main_frame, text="Descargar", command=self.start_download, state='disabled')
        self.download_button.grid(column=1, row=2, sticky=tk.E)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=300, mode='determinate', variable=self.progress)
        self.progress_bar.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E))

        # Etiqueta de estado
        ttk.Label(main_frame, textvariable=self.status).grid(column=0, row=4, columnspan=3, sticky=(tk.W, tk.E))

        # Configurar el grid
        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

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
            self.download_button['state'] = 'normal'
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo: {str(e)}")

    def start_download(self):
        self.download_button['state'] = 'disabled'
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        try:
            ruta_descarga = os.path.join(os.getcwd(), 'download')
            lineas = self.leer_archivo_mdl(self.file_path.get())
            data_lines = lineas[lineas.index("$data-start\n")+1:]
            self.descargar_archivos(data_lines, ruta_descarga)
            shutil.copy(self.file_path.get(), ruta_descarga)
            self.master.after(0, lambda: messagebox.showinfo("Éxito", "Descarga completa"))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Error durante la descarga: {str(e)}"))
        finally:
            self.master.after(0, lambda: self.download_button.config(state='normal'))

    def leer_archivo_mdl(self, ruta_archivo):
        with open(ruta_archivo, 'r') as archivo:
            return archivo.readlines()

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
                    valor = partes[1].rstrip(';').strip()
                    cabecera[clave] = valor
        return cabecera

    def mostrar_cabecera(self, cabecera):
        info = f"Nombre del paquete: {cabecera['Name']}\n"
        info += f"Versión: {cabecera['Version']}\n"
        info += f"Número de registro: {cabecera['NReg']}\n"
        info += f"Peso total: {cabecera['TotalSize']}\n"
        info += f"Número de archivos: {cabecera['TotalArchives']}\n"
        info += f"Autor: {cabecera['Author']}\n"
        info += f"Descripción: {cabecera['Description']}\n"
        
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state='disabled')

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
                    progress = (files_downloaded / total_files) * 100
                    self.master.after(0, lambda p=progress: self.progress.set(p))
                    self.master.after(0, lambda f=files_downloaded, t=total_files: 
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
                        percent = (downloaded / total_size) * 100
                        self.master.after(0, lambda p=percent: self.progress.set(p))

def main():
    root = tk.Tk()
    app = MDLDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
