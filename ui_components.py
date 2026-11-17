# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Chelo
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

import os
import sys
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMenuBar, QMenu, QAction, QDialog, QVBoxLayout, 
    QMessageBox, QWidget, QSizePolicy, QHBoxLayout, QPushButton, QToolBar, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from catalogo_componentes import CatalogoComponentes
from catalogo_datasheets import CatalogoDatasheets
from data_manager import exportar_datos_completos, importar_datos_completos, cargar_vinculaciones, guardar_vinculaciones

class ElectroCatalogApp(QMainWindow):
    def __init__(self, catalogo_datasheets=None):
        super().__init__()
        self.setWindowTitle("ElectroCatalog")
        self.resize(1100, 700) # Tamaño inicial de la ventana

        # Cargar vinculaciones al iniciar
        self.vinculaciones = cargar_vinculaciones()

        # Configuración del tema oscuro
        self.set_dark_theme()

        # Crear instancia de CatalogoDatasheets
        catalogo_datasheets_instancia = CatalogoDatasheets()
        # Crear instancia de CatalogoComponentes y pasarle la instancia de CatalogoDatasheets
        catalogo_componentes_instancia = CatalogoComponentes(catalogo_datasheets_instancia)
        # Agregar pestañas
        self.tabs = QTabWidget()
        self.tabs.addTab(catalogo_componentes_instancia, "Componentes")
        self.tabs.addTab(catalogo_datasheets_instancia, "Datasheets y Manuales")
        self.setCentralWidget(self.tabs)

        # Agregar menú desplegable y botón "Acerca de ElectroCatalog" en la misma línea
        self.crear_barra_superior()

    def crear_barra_superior(self):
        """Crea una barra superior con el menú 'Archivo' y el botón 'Acerca de ElectroCatalog'."""
        # Crear un contenedor para la barra superior
        barra_superior = QWidget()
        layout_superior = QHBoxLayout(barra_superior)
        layout_superior.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes

        # Crear el menú "Archivo"
        menubar = QMenuBar()
        menu_archivo = menubar.addMenu("Archivo")

        # Crear el menú "Vincular"
        menu_vincular = menubar.addMenu("Vincular")

        # Opción "Buscar Vínculos"
        accion_buscar_vinculos = QAction("Buscar Vínculos", self)
        accion_buscar_vinculos.triggered.connect(self.buscar_vinculos)
        menu_vincular.addAction(accion_buscar_vinculos)

        # Opción "Exportar Datos"
        accion_exportar = QAction("Exportar Datos", self)
        accion_exportar.triggered.connect(self.exportar_datos)
        menu_archivo.addAction(accion_exportar)

        # Opción "Importar Datos"
        accion_importar = QAction("Importar Datos", self)
        accion_importar.triggered.connect(self.importar_datos)
        menu_archivo.addAction(accion_importar)

        # Opción "Actualizar Datos"
        accion_actualizar = QAction("Actualizar Datos", self)
        accion_actualizar.triggered.connect(self.actualizar_datos)
        menu_archivo.addAction(accion_actualizar)

        # Agregar el menú al layout
        layout_superior.addWidget(menubar)

        # Espaciador para empujar el botón a la derecha
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout_superior.addWidget(spacer)

        # Botón "Acerca de ElectroCatalog"
        acerca_button = QPushButton("Acerca de ElectroCatalog", self)
        acerca_button.clicked.connect(self.mostrar_acerca)
        acerca_button.setStyleSheet("background-color: #353535; color: white; border-radius: 5px; padding: 5px;")
        layout_superior.addWidget(acerca_button)

        # Agregar la barra superior a la ventana principal
        self.setMenuWidget(barra_superior)

    def exportar_datos(self):
        """Maneja la exportación de datos."""
        archivo_zip, _ = QFileDialog.getSaveFileName(self, "Exportar datos", "ElectroCatalog_Backup.zip", "Archivos ZIP (*.zip)")
        if archivo_zip:
            if exportar_datos_completos(archivo_zip):
                QMessageBox.information(self, "Éxito", "Los datos se han exportado correctamente.")

    def importar_datos(self):
        """Maneja la importación de datos."""
        archivo_zip, _ = QFileDialog.getOpenFileName(self, "Importar datos", "", "Archivos ZIP (*.zip)")
        if archivo_zip:
            confirmacion = QMessageBox.question(
                self, 
                "Confirmar Importación", 
                "¿Estás seguro de que deseas importar los datos? Esto sobrescribirá los datos actuales.", 
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmacion == QMessageBox.Yes:
                if importar_datos_completos(archivo_zip):
                    QMessageBox.information(self, "Éxito", "Los datos se han importado correctamente.")
                    # Recargar los datos en la aplicación
                    self.actualizar_datos()

    def actualizar_datos(self):
        """Recarga los datos en los catálogos."""
        # Obtener las instancias de los catálogos
        catalogo_componentes = self.tabs.widget(0)  # Pestaña "Componentes"
        catalogo_datasheets = self.tabs.widget(1)   # Pestaña "Datasheets y Manuales"

        # Recargar los datos en los catálogos
        if hasattr(catalogo_componentes, "actualizar_lista"):
            catalogo_componentes.actualizar_lista()
        if hasattr(catalogo_datasheets, "actualizar_lista"):
            catalogo_datasheets.actualizar_lista()

        QMessageBox.information(self, "Datos Actualizados", "Los datos se han actualizado correctamente.")

    def set_dark_theme(self):
        """Aplica un tema oscuro a la interfaz y usa fuentes compatibles en Windows."""
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        
        # Usar fuente estándar compatible con Windows
        font = QFont("Segoe UI", 10)  # "Segoe UI" es la fuente estándar de Windows
        self.setFont(font)

        self.setPalette(palette)

    def mostrar_acerca(self):
        """Muestra información sobre la aplicación, incluyendo botones de donación."""
        mensaje = (
            "ElectroCatalog v2.0\n\n"
            "Desarrollado por Chelo\n\n"
            "Un catalogador de componentes electrónicos y datasheets para organizar tu colección.\n\n"
            "Si ElectroCatalog te ha sido útil, podés ayudarme a seguir mejorándolo con una donación.\n"
            "¡Tu apoyo significa mucho y hace la diferencia! ❤️"
        )

        # Crear el cuadro de diálogo
        acerca_dialog = QMessageBox(self)
        acerca_dialog.setWindowTitle("Acerca de ElectroCatalog")
        acerca_dialog.setText(mensaje)
        acerca_dialog.setStandardButtons(QMessageBox.Ok)

        # Botón para donar en PayPal
        boton_paypal = acerca_dialog.addButton("Donar en PayPal", QMessageBox.ActionRole)
        boton_paypal.clicked.connect(lambda: webbrowser.open("https://paypal.me/electrocatalog"))

        # Botón para donar en Ko-Fi
        boton_kofi = acerca_dialog.addButton("Donar en Ko-Fi", QMessageBox.ActionRole)
        boton_kofi.clicked.connect(lambda: webbrowser.open("https://ko-fi.com/electrocatalog"))

        acerca_dialog.exec_()

    def buscar_vinculos(self):
        """Busca coincidencias entre componentes y documentos, excluyendo las ya vinculadas."""
        # Cargar vinculaciones existentes
        vinculaciones_existentes = self.cargar_vinculaciones()
        existentes = set((v["componente"], v["documento"]) for v in vinculaciones_existentes)  # Pares ya vinculados

        # Obtener listas actualizadas
        nombres_componentes = list(self.tabs.widget(0).catalogo.keys())  # Componentes
        nombres_documentos = list(self.tabs.widget(1).catalogo.keys())   # Documentos

        # Buscar nuevas coincidencias no vinculadas
        coincidencias = []
        for componente in nombres_componentes:
            for documento in nombres_documentos:
                # Coincidencia parcial (ej: "CDS111" en "CDS111_manual.pdf")
                if componente.lower() in documento.lower() or documento.lower() in componente.lower():
                    # Excluir pares ya vinculados
                    if (componente, documento) not in existentes:  # <-- Filtro clave
                        coincidencias.append((componente, documento))

        # Mostrar diálogo solo si hay nuevas coincidencias
        if coincidencias:
            self.mostrar_dialogo_vinculos(coincidencias)
        else:
            QMessageBox.information(self, "Sin coincidencias", "¡Todos los vínculos posibles ya están confirmados!")
            
    def mostrar_dialogo_vinculos(self, coincidencias):
        """Muestra un diálogo para seleccionar las coincidencias a vincular."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Vínculos")
        layout = QVBoxLayout(dialog)

        # Crear una lista de checkboxes para las coincidencias
        self.checkboxes = []
        for componente, documento in coincidencias:
            checkbox = QCheckBox(f"{componente} <-> {documento}")
            self.checkboxes.append((checkbox, componente, documento))
            layout.addWidget(checkbox)

        # Botón para vincular las selecciones
        boton_vincular = QPushButton("Vincular Seleccionados")
        boton_vincular.clicked.connect(lambda: self.vincular_seleccionados(dialog))
        layout.addWidget(boton_vincular)

        dialog.exec_()

    def vincular_seleccionados(self, dialog):
        """Agrega nuevas vinculaciones sin eliminar las existentes."""
        # Cargar vinculaciones existentes
        vinculaciones_existentes = self.cargar_vinculaciones()
        
        # Obtener nuevas vinculaciones seleccionadas
        nuevas_vinculaciones = []
        for checkbox, componente, documento in self.checkboxes:
            if checkbox.isChecked():
                nuevas_vinculaciones.append({"componente": componente, "documento": documento})
        
        # Combinar con las existentes (evitando duplicados)
        for nueva in nuevas_vinculaciones:
            if nueva not in vinculaciones_existentes:  # <-- Evitar duplicados
                vinculaciones_existentes.append(nueva)
        
        # Guardar la lista completa
        if nuevas_vinculaciones:
            self.guardar_vinculaciones(vinculaciones_existentes)  # <-- Guardar todas
            QMessageBox.information(self, "Éxito", "Vinculaciones actualizadas correctamente.")
            # Actualizar la tabla de componentes
            catalogo_componentes = self.tabs.widget(0)
            if hasattr(catalogo_componentes, "actualizar_lista"):
                catalogo_componentes.actualizar_lista()
        else:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron nuevos vínculos.")

        dialog.close()

    

    
