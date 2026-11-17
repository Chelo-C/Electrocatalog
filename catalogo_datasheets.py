# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Chelo
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

import csv
import os
import shutil
import json
import subprocess
import sys
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QInputDialog, 
    QComboBox, QDialog, QFormLayout, QDialogButtonBox, QHeaderView
)
from PyQt5.QtCore import Qt
from data_manager import cargar_datos, guardar_datos
from appdirs import user_config_dir

# --- CONFIGURACIÓN DE RUTAS ---
CONFIG_DIR = user_config_dir("ElectroCatalog")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CATALOGO_DATASHEETS = os.path.join(CONFIG_DIR, "catalogo_datasheets.json")
PAPELERA_DATOS = os.path.join(CONFIG_DIR, "papelera_datos.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

CARPETA_DOCUMENTOS = os.path.join(CONFIG_DIR, "Documentos")
CARPETA_PAPELERA = os.path.join(CONFIG_DIR, "Papelera")

if not os.path.exists(CARPETA_DOCUMENTOS):
    os.makedirs(CARPETA_DOCUMENTOS)
if not os.path.exists(CARPETA_PAPELERA):
    os.makedirs(CARPETA_PAPELERA)

CARPETA_DESCARGAS = os.path.join(os.path.expanduser("~"), "Downloads")

# --- FUNCIONES DE CONFIGURACIÓN Y RUTAS ---
def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def actualizar_configuracion(**kwargs):
    """Actualiza claves en config.json sin borrar las existentes."""
    config = cargar_configuracion()
    config.update(kwargs)
    guardar_configuracion(config)

def cargar_configuracion():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def get_ruta_absoluta(ruta_relativa):
    if not ruta_relativa or os.path.isabs(ruta_relativa):
        return ruta_relativa
    return os.path.join(CARPETA_DOCUMENTOS, ruta_relativa)

def get_ruta_relativa(ruta_absoluta):
    if not ruta_absoluta or not os.path.isabs(ruta_absoluta):
        return ruta_absoluta
    try:
        return os.path.relpath(ruta_absoluta, CARPETA_DOCUMENTOS)
    except ValueError:
        return ruta_absoluta

# --- DIÁLOGOS DE LA INTERFAZ ---
class DatasheetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Datasheet")
        self.setModal(True)
        layout = QFormLayout(self)
        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Nombre del componente")
        layout.addRow("Nombre:", self.nombre_edit)
        self.fabricante_edit = QLineEdit()
        self.fabricante_edit.setPlaceholderText("Fabricante (opcional)")
        layout.addRow("Fabricante:", self.fabricante_edit)
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(["Datasheets", "Manuales de Servicio", "Manuales de Usuario"])
        layout.addRow("Categoría:", self.categoria_combo)
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def get_datos(self):
        nombre = self.nombre_edit.text().strip()
        fabricante = self.fabricante_edit.text().strip()
        categoria = self.categoria_combo.currentText()
        return {"nombre": nombre, "fabricante": fabricante if fabricante else "Sin definir", "categoria": categoria}

class ModificarDatasheetDialog(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Datasheet")
        self.datos = datos
        layout = QFormLayout(self)
        self.nombre_edit = QLineEdit(self.datos.get("componente", ""))
        layout.addRow("Nombre:", self.nombre_edit)
        self.fabricante_edit = QLineEdit(self.datos.get("fabricante", ""))
        layout.addRow("Fabricante:", self.fabricante_edit)
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(["Datasheets", "Manuales de Servicio", "Manuales de Usuario"])
        self.categoria_combo.setCurrentText(self.datos.get("categoria", ""))
        layout.addRow("Categoría:", self.categoria_combo)
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def get_datos(self):
        return {"componente": self.nombre_edit.text().strip(), "fabricante": self.fabricante_edit.text().strip(), "categoria": self.categoria_combo.currentText()}

# --- CLASE PRINCIPAL DEL CATÁLOGO ---
class CatalogoDatasheets(QWidget):
    def __init__(self):
        super().__init__()
        self._migrar_rutas_a_relativas()
        self.catalogo = cargar_datos(CATALOGO_DATASHEETS)
        self.papelera_datos = cargar_datos(PAPELERA_DATOS)
        config = cargar_configuracion()
        self.ultima_ruta = config.get("ultima_ruta", CARPETA_DESCARGAS)
        self.setup_ui()
        self.actualizar_lista()

    def setup_ui(self):
        layout_principal = QVBoxLayout(self)
        barra_superior = QHBoxLayout()
        self.entry_buscar = QLineEdit()
        self.entry_buscar.setPlaceholderText("Buscar documento...")
        self.entry_buscar.textChanged.connect(self.actualizar_lista)
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "Datasheets", "Manuales de Servicio", "Manuales de Usuario"])
        self.combo_filtro.currentIndexChanged.connect(self.actualizar_lista)
        boton_agregar = QPushButton("Agregar")
        boton_agregar.clicked.connect(self.agregar_datasheet)
        boton_modificar = QPushButton("Modificar")
        boton_modificar.clicked.connect(self.modificar_datasheet)
        boton_eliminar = QPushButton("Eliminar")
        boton_eliminar.clicked.connect(self.eliminar_datasheet)
        boton_exportar = QPushButton("Exportar a CSV")
        boton_exportar.clicked.connect(self.exportar_csv)
        barra_superior.addWidget(self.entry_buscar)
        barra_superior.addWidget(self.combo_filtro)
        barra_superior.addWidget(boton_agregar)
        barra_superior.addWidget(boton_modificar)
        barra_superior.addWidget(boton_eliminar)
        barra_superior.addWidget(boton_exportar)
        layout_principal.addLayout(barra_superior)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Componente", "Fabricante", "Categoría", "Ruta (Relativa)"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.doubleClicked.connect(self.abrir_documento)
        self.tabla.keyPressEvent = self.keyPressEvent
        layout_principal.addWidget(self.tabla)

    def _migrar_rutas_a_relativas(self):
        config = cargar_configuracion()
        if config.get("rutas_migradas_a_relativas"):
            return
        catalogo = cargar_datos(CATALOGO_DATASHEETS)
        papelera = cargar_datos(PAPELERA_DATOS)
        for cat in [catalogo, papelera]:
            for key, value in cat.items():
                if os.path.isabs(value.get("ruta", "")):
                    value["ruta"] = get_ruta_relativa(value["ruta"])
        guardar_datos(CATALOGO_DATASHEETS, catalogo)
        guardar_datos(PAPELERA_DATOS, papelera)
        config["rutas_migradas_a_relativas"] = True
        guardar_configuracion(config)
        print("Migración de rutas a relativas completada.")

    def abrir_archivo(self, ruta_absoluta):
        if not os.path.exists(ruta_absoluta):
            QMessageBox.warning(self, "Error", f"El archivo no existe.\n{ruta_absoluta}")
            return
        if sys.platform.startswith("win"):
            os.startfile(ruta_absoluta)
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", ruta_absoluta])
        else:
            QMessageBox.warning(self, "Error", "Sistema operativo no soportado.")

    def abrir_documento(self, index):
        ruta_relativa = self.tabla.item(index.row(), 3).text()
        ruta_absoluta = get_ruta_absoluta(ruta_relativa)
        if not os.path.exists(ruta_absoluta):
            nombre_archivo = os.path.basename(ruta_absoluta)
            if nombre_archivo in self.papelera_datos:
                if self.restaurar_datasheet(nombre_archivo):
                    QMessageBox.information(self, "Restaurado", f"El documento {nombre_archivo} fue restaurado.")
                    ruta_relativa_restaurada = self.catalogo[nombre_archivo]["ruta"]
                    self.abrir_archivo(get_ruta_absoluta(ruta_relativa_restaurada))
            else:
                QMessageBox.warning(self, "Error", f"El archivo no existe.\n{ruta_absoluta}")
            return
        self.abrir_archivo(ruta_absoluta)

    def agregar_datasheet(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(self.ultima_ruta)
        if file_dialog.exec_():
            archivo_seleccionado = file_dialog.selectedFiles()[0]
            if not archivo_seleccionado: return
            self.ultima_ruta = os.path.dirname(archivo_seleccionado)
            actualizar_configuracion(ultima_ruta=self.ultima_ruta)
            dialogo = DatasheetDialog(self)
            if dialogo.exec_() == QDialog.Accepted:
                datos = dialogo.get_datos()
                if not datos["nombre"]:
                    QMessageBox.warning(self, "Error", "El nombre del componente es obligatorio.")
                    return
                carpeta_categoria = os.path.join(CARPETA_DOCUMENTOS, datos["categoria"])
                if not os.path.exists(carpeta_categoria):
                    os.makedirs(carpeta_categoria)
                nombre_archivo_nuevo = f"{datos['nombre']}_{datos['fabricante']}{os.path.splitext(archivo_seleccionado)[1]}"
                ruta_destino_abs = os.path.join(carpeta_categoria, nombre_archivo_nuevo)
                shutil.copy(archivo_seleccionado, ruta_destino_abs)
                self.catalogo[nombre_archivo_nuevo] = {
                    "componente": datos["nombre"],
                    "fabricante": datos["fabricante"],
                    "categoria": datos["categoria"],
                    "ruta": get_ruta_relativa(ruta_destino_abs)
                }
                guardar_datos(CATALOGO_DATASHEETS, self.catalogo)
                self.actualizar_lista()
                QMessageBox.information(self, "Éxito", f"Documento {nombre_archivo_nuevo} agregado.")

    def actualizar_lista(self):
        self.catalogo = cargar_datos(CATALOGO_DATASHEETS)
        busqueda = self.entry_buscar.text().lower()
        filtro = self.combo_filtro.currentText()
        self.tabla.setRowCount(0)
        for nombre, datos in self.catalogo.items():
            if (busqueda and busqueda not in nombre.lower() and busqueda not in datos.get("componente", "").lower()):
                continue
            if filtro != "Todos" and datos.get("categoria") != filtro:
                continue
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(datos.get("componente", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(datos.get("fabricante", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(datos.get("categoria", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(datos.get("ruta", "")))
        if self.tabla.rowCount() > 0:
            self.tabla.selectRow(0)

    def modificar_datasheet(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione un documento para modificar.")
            return
        ruta_relativa_actual = self.tabla.item(fila, 3).text()
        clave_catalogo = None
        for clave, datos in self.catalogo.items():
            if datos.get("ruta") == ruta_relativa_actual:
                clave_catalogo = clave
                break
        if not clave_catalogo:
            QMessageBox.warning(self, "Error", "El documento no se encontró en el catálogo.")
            return
        datos_actuales = self.catalogo[clave_catalogo]
        dialogo = ModificarDatasheetDialog(datos_actuales, self)
        if dialogo.exec_() == QDialog.Accepted:
            nuevos_datos = dialogo.get_datos()
            if not nuevos_datos["componente"]:
                QMessageBox.warning(self, "Error", "El nombre del componente es obligatorio.")
                return
            ruta_abs_actual = get_ruta_absoluta(ruta_relativa_actual)
            nuevo_nombre_base = f"{nuevos_datos['componente']}_{nuevos_datos['fabricante']}{os.path.splitext(clave_catalogo)[1]}"
            nueva_carpeta_cat = os.path.join(CARPETA_DOCUMENTOS, nuevos_datos["categoria"])
            if not os.path.exists(nueva_carpeta_cat):
                os.makedirs(nueva_carpeta_cat)
            nueva_ruta_abs = os.path.join(nueva_carpeta_cat, nuevo_nombre_base)
            if ruta_abs_actual != nueva_ruta_abs:
                try:
                    shutil.move(ruta_abs_actual, nueva_ruta_abs)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo mover el archivo: {e}")
                    return
            del self.catalogo[clave_catalogo]
            self.catalogo[nuevo_nombre_base] = {
                "componente": nuevos_datos["componente"],
                "fabricante": nuevos_datos["fabricante"],
                "categoria": nuevos_datos["categoria"],
                "ruta": get_ruta_relativa(nueva_ruta_abs)
            }
            guardar_datos(CATALOGO_DATASHEETS, self.catalogo)
            self.actualizar_lista()
            QMessageBox.information(self, "Éxito", "Documento modificado correctamente.")

    def eliminar_datasheet(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione un documento para eliminar.")
            return
        ruta_relativa = self.tabla.item(fila, 3).text()
        ruta_absoluta = get_ruta_absoluta(ruta_relativa)
        nombre_base = os.path.basename(ruta_absoluta)
        if QMessageBox.question(self, "Confirmar", f"¿Enviar {nombre_base} a la papelera?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        clave_catalogo = None
        for clave, datos in self.catalogo.items():
            if datos.get("ruta") == ruta_relativa:
                clave_catalogo = clave
                break
        if not clave_catalogo:
            QMessageBox.warning(self, "Error", "No se encontró el archivo en el catálogo.")
            return
        if os.path.exists(ruta_absoluta):
            shutil.move(ruta_absoluta, os.path.join(CARPETA_PAPELERA, nombre_base))
        self.papelera_datos[clave_catalogo] = self.catalogo[clave_catalogo]
        del self.catalogo[clave_catalogo]
        guardar_datos(PAPELERA_DATOS, self.papelera_datos)
        guardar_datos(CATALOGO_DATASHEETS, self.catalogo)
        self.actualizar_lista()
        QMessageBox.information(self, "Eliminado", f"{nombre_base} movido a la papelera.")

    def vaciar_papelera(self):
        if QMessageBox.question(self, "Vaciar Papelera", "¿Vaciar la papelera? Esta acción no se puede deshacer.", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        try:
            for archivo in os.listdir(CARPETA_PAPELERA):
                os.remove(os.path.join(CARPETA_PAPELERA, archivo))
            self.papelera_datos = {}
            guardar_datos(PAPELERA_DATOS, self.papelera_datos)
            QMessageBox.information(self, "Éxito", "La papelera ha sido vaciada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al vaciar la papelera:\n{e}")
            
    def restaurar_datasheet(self, nombre_archivo):
        if nombre_archivo not in self.papelera_datos:
            return False
        datos_originales = self.papelera_datos[nombre_archivo]
        ruta_papelera_abs = os.path.join(CARPETA_PAPELERA, nombre_archivo)
        ruta_original_abs = get_ruta_absoluta(datos_originales["ruta"])
        os.makedirs(os.path.dirname(ruta_original_abs), exist_ok=True)
        if os.path.exists(ruta_papelera_abs):
            shutil.move(ruta_papelera_abs, ruta_original_abs)
        self.catalogo[nombre_archivo] = datos_originales
        del self.papelera_datos[nombre_archivo]
        guardar_datos(PAPELERA_DATOS, self.papelera_datos)
        guardar_datos(CATALOGO_DATASHEETS, self.catalogo)
        self.actualizar_lista()
        return True
    
    def exportar_csv(self):
        archivo_csv, _ = QFileDialog.getSaveFileName(self, "Guardar como", "catalogo_datasheets.csv", "Archivos CSV (*.csv)")
        if not archivo_csv: return
        try:
            with open(archivo_csv, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Componente", "Fabricante", "Categoría", "Ruta Relativa"])
                for _, datos in self.catalogo.items():
                    writer.writerow([datos.get("componente"), datos.get("fabricante"), datos.get("categoria"), datos.get("ruta")])
            QMessageBox.information(self, "Éxito", f"Catálogo exportado a {archivo_csv}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar el CSV:\n{e}")
