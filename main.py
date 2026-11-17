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