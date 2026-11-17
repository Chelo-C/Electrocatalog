import json
import os
import zipfile
import shutil
from PyQt5.QtWidgets import QMessageBox
from appdirs import user_config_dir  # Para obtener el directorio de configuración del usuario

# Obtener el directorio de configuración del usuario
CONFIG_DIR = user_config_dir("ElectroCatalog")

# Archivos de datos
CATALOGO_COMPONENTES = os.path.join(CONFIG_DIR, "catalogo_componentes.json")
CATALOGO_DATASHEETS = os.path.join(CONFIG_DIR, "catalogo_datasheets.json")
PAPELERA_DATOS = os.path.join(CONFIG_DIR, "papelera_datos.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Carpetas de documentos y papelera
CARPETA_DOCUMENTOS = os.path.join(CONFIG_DIR, "Documentos")
CARPETA_PAPELERA = os.path.join(CONFIG_DIR, "Papelera")

# Crear el directorio de configuración si no existe
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# Crear las carpetas de documentos y papelera si no existen
if not os.path.exists(CARPETA_DOCUMENTOS):
    os.makedirs(CARPETA_DOCUMENTOS)

if not os.path.exists(CARPETA_PAPELERA):
    os.makedirs(CARPETA_PAPELERA)

def cargar_datos(archivo):
    """Carga los datos desde un archivo JSON."""
    try:
        with open(archivo, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def guardar_datos(archivo, datos):
    """Guarda los datos en un archivo JSON."""
    with open(archivo, "w") as file:
        json.dump(datos, file, indent=4)

def exportar_datos_completos(destino_zip):
    """
    Exporta todos los datos (archivos JSON, vinculaciones y carpeta de documentos) a un archivo ZIP.
    """
    try:
        with zipfile.ZipFile(destino_zip, 'w') as zipf:
            # Archivos JSON a incluir (¡AGREGAMOS VINCULACIONES!)
            archivos_json = [
                CATALOGO_COMPONENTES,
                CATALOGO_DATASHEETS,
                PAPELERA_DATOS,
                CONFIG_FILE,
                os.path.join(CONFIG_DIR, "vinculaciones.json")  # Nuevo archivo
            ]

            # Agregar archivos JSON
            for archivo in archivos_json:
                if os.path.exists(archivo):
                    zipf.write(archivo, os.path.basename(archivo))

            # Agregar carpeta de documentos
            if os.path.exists(CARPETA_DOCUMENTOS):
                for root, dirs, files in os.walk(CARPETA_DOCUMENTOS):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=CONFIG_DIR)
                        zipf.write(file_path, arcname)

        return True
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al exportar: {str(e)}")
        return False

def importar_datos_completos(origen_zip):
    """
    Importa todos los datos (archivos JSON, vinculaciones y carpeta de documentos) desde un archivo ZIP.
    """
    try:
        with zipfile.ZipFile(origen_zip, 'r') as zipf:
            # Extraer todo en el directorio de configuración
            zipf.extractall(CONFIG_DIR)

        print(f"Datos importados correctamente desde: {origen_zip}")
        return True
    except Exception as e:
        print(f"Error al importar datos: {str(e)}")
        QMessageBox.critical(None, "Error", f"Error al importar datos: {str(e)}")
        return False

def guardar_vinculaciones(vinculaciones):
    """Guarda las vinculaciones en un archivo JSON."""
    VINCULACIONES_FILE = os.path.join(CONFIG_DIR, "vinculaciones.json")
    guardar_datos(VINCULACIONES_FILE, vinculaciones)

def cargar_vinculaciones():
    """Carga las vinculaciones desde un archivo JSON."""
    VINCULACIONES_FILE = os.path.join(CONFIG_DIR, "vinculaciones.json")
    return cargar_datos(VINCULACIONES_FILE)
