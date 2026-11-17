# ElectroCatalog - Un catalogador de componentes electrónicos.
# Copyright (C) 2026 Chelo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui_components import ElectroCatalogApp  # Asegúrate de importar la ventana principal

if __name__ == "__main__":
    # Crear la aplicación
    app = QApplication(sys.argv)

    # Ajustar DPI para mejorar la apariencia en pantallas de alta resolución en Windows
    if sys.platform.startswith("win"):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Mejora escalado en Windows

    # Ajustar fuente estándar compatible con Windows
    font = QFont("Segoe UI", 10)  # Fuente estándar de Windows
    app.setFont(font)

    # Aplicar un estilo más uniforme entre Linux y Windows
    app.setStyle("Fusion")

    # Crear y mostrar la ventana principal
    ventana = ElectroCatalogApp()
    ventana.show()

    # Ejecutar la aplicación
    sys.exit(app.exec_())