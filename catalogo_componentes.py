# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Chelo
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

import catalogo_datasheets
import csv
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QInputDialog, QFormLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView
import catalogo_datasheets
from data_manager import cargar_datos, guardar_datos, cargar_vinculaciones
from appdirs import user_config_dir  # Para obtener el directorio de configuración del usuario

# Obtener el directorio de configuración del usuario
CONFIG_DIR = user_config_dir("ElectroCatalog")  # Esto devuelve ~/.config/ElectroCatalog en Linux o %APPDATA%/ElectroCatalog en Windows

# Crear el directorio de configuración si no existe
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# Archivo de datos de componentes
CATALOGO_COMPONENTES = os.path.join(CONFIG_DIR, "catalogo_componentes.json")

class CatalogoComponentes(QWidget):
    def __init__(self, catalogo_datasheets=None):
        super().__init__()

        # Guardar la instancia de CatalogoDatasheets
        self.catalogo_datasheets = catalogo_datasheets  # <-- Guardar la instancia

        # Cargar los datos desde el archivo JSON
        self.catalogo = cargar_datos(CATALOGO_COMPONENTES)

        # Cargar vinculaciones
        self.vinculaciones = cargar_vinculaciones()

        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # Barra de control
        barra_superior = QHBoxLayout()

        # Campo de búsqueda
        self.entry_buscar = QLineEdit()
        self.entry_buscar.setPlaceholderText("Buscar componente...")
        self.entry_buscar.textChanged.connect(self.actualizar_lista)
        barra_superior.addWidget(self.entry_buscar, stretch=4)  # Ocupa la mayor parte del espacio

        # Desplegable de categorías
        self.combo_categorias = QComboBox()
        self.combo_categorias.addItem("Todas las categorías")  # Opción por defecto
        self.combo_categorias.currentIndexChanged.connect(self.actualizar_lista)
        barra_superior.addWidget(self.combo_categorias, stretch=2)  # Ocupa menos espacio que la búsqueda

        # Campo de cantidad
        self.entry_cantidad = QLineEdit()
        self.entry_cantidad.setPlaceholderText("Cantidad")
        self.entry_cantidad.setFixedWidth(80)  # Ancho fijo para el campo de cantidad
        barra_superior.addWidget(self.entry_cantidad)

        # Botones
        boton_agregar = QPushButton("Agregar")
        boton_agregar.clicked.connect(self.agregar_componente)
        barra_superior.addWidget(boton_agregar)

        boton_quitar = QPushButton("Quitar")
        boton_quitar.clicked.connect(self.quitar_componente)
        barra_superior.addWidget(boton_quitar)

        boton_modificar = QPushButton("Modificar")
        boton_modificar.clicked.connect(self.modificar_componente)
        barra_superior.addWidget(boton_modificar)

        boton_exportar = QPushButton("Exportar a CSV")
        boton_exportar.clicked.connect(self.exportar_csv)
        barra_superior.addWidget(boton_exportar)

        layout_principal.addLayout(barra_superior)

        # Tabla de componentes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)  # Añadir una columna adicional para los documentos vinculados
        self.tabla.setHorizontalHeaderLabels(["Modelo", "Cantidad", "Categoría", "Detalles", "Ubicación", "Datasheet"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # Deshabilitar redimensionamiento manual
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.itemClicked.connect(self.seleccionar_componente)
        layout_principal.addWidget(self.tabla)

        # Conectar el doble clic en la columna de documentos vinculados
        self.tabla.itemDoubleClicked.connect(self.abrir_documento_vinculado)  # <-- Mover aquí

        # Ajustar el ancho de las columnas según los porcentajes
        self.ajustar_ancho_columnas()

        # Actualizar lista de categorías
        self.actualizar_categorias()
        self.actualizar_lista()

    def ajustar_ancho_columnas(self):
        """Ajusta el ancho de las columnas respetando proporciones."""
        ancho_total = self.tabla.viewport().width()  # Ancho total disponible en la tabla
        self.tabla.setColumnWidth(0, int(ancho_total * 0.10))  # Modelo: 10%
        self.tabla.setColumnWidth(1, int(ancho_total * 0.10))  # Cantidad: 10%
        self.tabla.setColumnWidth(2, int(ancho_total * 0.20))  # Categoría: 20%
        self.tabla.setColumnWidth(3, int(ancho_total * 0.35))  # Detalles: 35%
        self.tabla.setColumnWidth(4, int(ancho_total * 0.15))  # Ubicación: 15%
        self.tabla.setColumnWidth(5, int(ancho_total * 0.10))  # Documentos Vinculados: 10%

    def resizeEvent(self, event):
        """Ajusta las columnas cuando la ventana cambia de tamaño."""
        super().resizeEvent(event)
        self.ajustar_ancho_columnas()

    def keyPressEvent(self, event):
        """Maneja el evento de presionar una tecla."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.mostrar_detalles_componente_con_teclado()
        else:
            super().keyPressEvent(event)

    def mostrar_detalles_componente_con_teclado(self):
        """Muestra los detalles del componente seleccionado cuando se presiona Enter."""
        seleccion = self.tabla.currentRow()
        if seleccion == -1:
            return  # No hay fila seleccionada

        modelo = self.tabla.item(seleccion, 0).text()
        datos = self.catalogo.get(modelo, {})
        if not datos:
            return

    def exportar_csv(self):
        """Exporta la lista de componentes a un archivo CSV."""
        archivo_csv, _ = QFileDialog.getSaveFileName(self, "Guardar como", "catalogo_componentes.csv", "Archivos CSV (*.csv)")
    
        if not archivo_csv:  # Si el usuario cancela, no hacemos nada
            return

        with open(archivo_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Modelo", "Cantidad", "Categoría", "Detalles", "Ubicación"])

            for modelo, datos in self.catalogo.items():
                detalles = ", ".join(f"{k}: {v}" for k, v in datos.get("detalles", {}).items())
                writer.writerow([modelo, datos.get("cantidad", 0), datos.get("categoria", ""), detalles, datos.get("ubicacion", "")])

        QMessageBox.information(self, "Exportación Exitosa", f"El catálogo se ha guardado en {archivo_csv}.")

    def actualizar_categorias(self):
        """Actualiza el desplegable de categorías con las categorías existentes en el catálogo."""
        categorias = set()
        for datos in self.catalogo.values():
            categoria = datos.get("categoria", "")
            if categoria:
                categorias.add(categoria)
        
        self.combo_categorias.clear()
        self.combo_categorias.addItem("Todas las categorías")  # Opción por defecto
        self.combo_categorias.addItems(sorted(categorias))

    def actualizar_lista(self):
        """Recarga los datos desde el archivo JSON y actualiza la tabla."""
        self.catalogo = cargar_datos(CATALOGO_COMPONENTES)
        self.vinculaciones = cargar_vinculaciones()

        busqueda = self.entry_buscar.text().lower()
        categoria_seleccionada = self.combo_categorias.currentText()

        self.tabla.setRowCount(0)
        for modelo, datos in self.catalogo.items():
            # Filtro por búsqueda
            if busqueda and busqueda not in modelo.lower():
                continue
            # Filtro por categoría
            if categoria_seleccionada != "Todas las categorías" and datos.get("categoria", "") != categoria_seleccionada:
                continue

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(modelo))
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(datos.get("cantidad", 0))))
            self.tabla.setItem(fila, 2, QTableWidgetItem(datos.get("categoria", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(", ".join([f"{k}: {v}" for k, v in datos.get("detalles", {}).items()])))
            self.tabla.setItem(fila, 4, QTableWidgetItem(datos.get("ubicacion", "")))

            # Mostrar documentos vinculados
            documentos_vinculados = [v["documento"] for v in self.vinculaciones if v["componente"] == modelo]
            item_vinculados = QTableWidgetItem(", ".join(documentos_vinculados))
            item_vinculados.setData(Qt.UserRole, documentos_vinculados)  # Guardar la lista de documentos vinculados
            self.tabla.setItem(fila, 5, item_vinculados)

        # Conectar el doble clic en la columna de documentos vinculados
        self.tabla.itemDoubleClicked.connect(self.abrir_documento_vinculado)

    def abrir_documento_vinculado(self, item):
        """Abre el documento vinculado cuando se hace doble clic en la columna correspondiente."""
        if item.column() != 5 or not self.catalogo_datasheets: 
            return

        documentos_vinculados = item.data(Qt.UserRole)
        if not documentos_vinculados:
            return

        documento_a_abrir = documentos_vinculados[0]

        for nombre_doc, datos_doc in self.catalogo_datasheets.catalogo.items():
            if nombre_doc.strip().lower() == documento_a_abrir.strip().lower():
                ruta_rel = datos_doc.get("ruta")
                ruta_abs = catalogo_datasheets.get_ruta_absoluta(ruta_rel)   # <-- resolver
                if ruta_abs and os.path.exists(ruta_abs):
                    self.catalogo_datasheets.abrir_archivo(ruta_abs)
                    return
                else:
                    QMessageBox.warning(self, "Error", f"La ruta del archivo no existe o es inválida:\n{ruta_abs}")
                    return

        QMessageBox.warning(self, "Error", f"No se pudo encontrar el documento vinculado:\n{documento_a_abrir}")

    

    

    def seleccionar_componente(self, item):
        """Selecciona un componente de la tabla y lo muestra en el campo de búsqueda."""
        if item.column() == 0:  # Solo nos interesa la columna del modelo
            self.entry_buscar.setText(item.text())

    def mostrar_detalles_componente(self, item):
        """Muestra los detalles de un componente en una ventana emergente."""
        if item.column() == 0:  # Solo nos interesa la columna del modelo
            modelo = item.text()
            datos = self.catalogo.get(modelo, {})
            if not datos:
                return

            # Crear una ventana emergente
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detalles de {modelo}")
            layout = QFormLayout(dialog)

            # Mostrar los detalles del componente
            layout.addRow(QLabel(f"Modelo: {modelo}"))
            layout.addRow(QLabel(f"Cantidad: {datos.get('cantidad', 0)}"))
            layout.addRow(QLabel(f"Categoría: {datos.get('categoria', '')}"))
            layout.addRow(QLabel(f"Ubicación: {datos.get('ubicacion', '')}"))

            detalles = datos.get("detalles", {})
            for key, value in detalles.items():
                layout.addRow(QLabel(f"{key.capitalize()}: {value}"))

            # Botón para cerrar la ventana
            boton_cerrar = QPushButton("Cerrar")
            boton_cerrar.clicked.connect(dialog.close)
            layout.addRow(boton_cerrar)

            dialog.exec_()

    def mostrar_dialogo_detalles(self, categoria_actual="", detalles_actuales={}, ubicacion_actual=""):
        """Muestra un diálogo para ingresar o modificar categoría, detalles y ubicación."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Detalles del Componente")
        layout = QFormLayout(dialog)

        # Campo de categoría
        combo_categoria = QComboBox()
        categorias = set()
        for datos in self.catalogo.values():
            categoria = datos.get("categoria", "")
            if categoria:
                categorias.add(categoria)
        combo_categoria.addItems(sorted(categorias))
        combo_categoria.addItem("Agregar nueva categoría")
        if categoria_actual:
            combo_categoria.setCurrentText(categoria_actual)
        layout.addRow("Categoría:", combo_categoria)

        # Campos de detalles
        entry_voltaje = QLineEdit()
        entry_voltaje.setPlaceholderText("Voltaje")
        if "voltaje" in detalles_actuales:
            entry_voltaje.setText(detalles_actuales["voltaje"])
        layout.addRow("Voltaje:", entry_voltaje)

        entry_corriente = QLineEdit()
        entry_corriente.setPlaceholderText("Corriente")
        if "corriente" in detalles_actuales:
            entry_corriente.setText(detalles_actuales["corriente"])
        layout.addRow("Corriente:", entry_corriente)

        entry_potencia = QLineEdit()
        entry_potencia.setPlaceholderText("Potencia")
        if "potencia" in detalles_actuales:
            entry_potencia.setText(detalles_actuales["potencia"])
        layout.addRow("Potencia:", entry_potencia)

        # Campo de ubicación
        entry_ubicacion = QLineEdit()
        entry_ubicacion.setPlaceholderText("Ubicación")
        entry_ubicacion.setText(ubicacion_actual)
        layout.addRow("Ubicación:", entry_ubicacion)

        # Botones de aceptar y cancelar
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
        botones.accepted.connect(dialog.accept)
        botones.rejected.connect(dialog.reject)
        layout.addRow(botones)

        if dialog.exec_() == QDialog.Accepted:
            categoria = combo_categoria.currentText()
            if categoria == "Agregar nueva categoría":
                nueva_categoria, ok = QInputDialog.getText(self, "Nueva Categoría", "Ingrese la nueva categoría:")
                if ok and nueva_categoria.strip():
                    categoria = nueva_categoria.strip()
                else:
                    return None

            detalles = {}
            if entry_voltaje.text().strip():
                detalles["voltaje"] = entry_voltaje.text().strip()
            if entry_corriente.text().strip():
                detalles["corriente"] = entry_corriente.text().strip()
            if entry_potencia.text().strip():
                detalles["potencia"] = entry_potencia.text().strip()

            ubicacion = entry_ubicacion.text().strip()

            return {
                "categoria": categoria,
                "detalles": detalles,
                "ubicacion": ubicacion
            }
        else:
            return None

    def agregar_componente(self):
        """Agrega un nuevo componente al catálogo."""
        modelo = self.entry_buscar.text().strip()
        if not modelo:
            QMessageBox.warning(self, "Error", "El campo de búsqueda está vacío.")
            return

        cantidad_texto = self.entry_cantidad.text().strip()
        if not cantidad_texto.isdigit():
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número válido.")
            return

        cantidad = int(cantidad_texto)

        # Verificar si el componente ya existe en el catálogo
        if modelo in self.catalogo:
            # Ventana de confirmación para agregar cantidad
            confirmacion = QMessageBox.question(
                self, 
                "Confirmar", 
                f"¿Está seguro de agregar {cantidad} unidades al componente {modelo}?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirmacion == QMessageBox.No:
                return  # El usuario canceló la acción

            # Si el componente ya existe, solo sumar la cantidad
            self.catalogo[modelo]["cantidad"] += cantidad
        else:
            # Si el componente no existe, mostrar el diálogo para ingresar detalles
            datos = self.mostrar_dialogo_detalles()
            if not datos:
                return  # El usuario canceló el diálogo

            # Agregar el nuevo componente al catálogo
            self.catalogo[modelo] = {
                "cantidad": cantidad,
                "categoria": datos["categoria"],
                "detalles": datos["detalles"],
                "ubicacion": datos["ubicacion"]
            }

        # Guardar los cambios y actualizar la lista
        guardar_datos(CATALOGO_COMPONENTES, self.catalogo)
        self.actualizar_categorias()
        self.actualizar_lista()

    def modificar_componente(self):
        """Modifica la categoría, detalles y ubicación de un componente seleccionado."""
        seleccion = self.tabla.currentRow()
        if seleccion == -1:
            QMessageBox.warning(self, "Error", "Seleccione un componente para modificar.")
            return

        modelo = self.tabla.item(seleccion, 0).text()
        datos_actuales = self.catalogo[modelo]

        # Mostrar diálogo para modificar categoría, detalles y ubicación
        datos = self.mostrar_dialogo_detalles(
            categoria_actual=datos_actuales.get("categoria", ""),
            detalles_actuales=datos_actuales.get("detalles", {}),
            ubicacion_actual=datos_actuales.get("ubicacion", "")
        )
        if not datos:
            return  # El usuario canceló el diálogo

        # Actualizar los datos del componente
        self.catalogo[modelo]["categoria"] = datos["categoria"]
        self.catalogo[modelo]["detalles"] = datos["detalles"]
        self.catalogo[modelo]["ubicacion"] = datos["ubicacion"]

        guardar_datos(CATALOGO_COMPONENTES, self.catalogo)
        self.actualizar_categorias()
        self.actualizar_lista()

    def quitar_componente(self):
        """Reduce la cantidad de un componente seleccionado."""
        seleccion = self.tabla.currentRow()
        if seleccion == -1:
            QMessageBox.warning(self, "Error", "Seleccione un componente para quitar.")
            return

        modelo = self.tabla.item(seleccion, 0).text()
        cantidad_texto = self.entry_cantidad.text().strip()
        if not cantidad_texto.isdigit():
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número válido.")
            return

        cantidad = int(cantidad_texto)
        if self.catalogo[modelo]["cantidad"] < cantidad:
            QMessageBox.warning(self, "Error", "La cantidad a quitar excede las unidades disponibles.")
            return

        # Ventana de confirmación para quitar cantidad
        confirmacion = QMessageBox.question(
            self, 
            "Confirmar", 
            f"¿Está seguro de quitar {cantidad} unidades del componente {modelo}?", 
            QMessageBox.Yes | QMessageBox.No
        )
    
        if confirmacion == QMessageBox.No:
            return  # El usuario canceló la acción

        self.catalogo[modelo]["cantidad"] -= cantidad

        if self.catalogo[modelo]["cantidad"] == 0:
            del self.catalogo[modelo]

        guardar_datos(CATALOGO_COMPONENTES, self.catalogo)
        self.actualizar_categorias()
        self.actualizar_lista()
