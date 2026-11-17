# 🔌 ElectroCatalog 2.0

Un catalogador de componentes electrónicos y datasheets para organizar tu colección de forma eficiente.

---

## 📝 Descripción

**ElectroCatalog** es una aplicación de escritorio (PyQt5) diseñada para ayudarte a gestionar y organizar tus componentes electrónicos y sus hojas de datos (datasheets). Con una interfaz moderna y tema oscuro, permite:

- Agregar, eliminar y buscar componentes.
- Gestionar los documentos (datasheets, manuales) asociados.
- Vincular automáticamente componentes con sus documentos correspondientes.
- Exportar e importar tus datos en formato ZIP para respaldos o transferencias.
- Buscar coincidencias parciales entre componentes y documentos para crear vínculos rápidamente.

---

## ✨ Características

- **Interfaz de dos pestañas:** "Componentes" y "Datasheets y Manuales".
- **Tema oscuro personalizado** para reducir la fatiga visual.
- **Búsqueda de vínculos:** Detecta coincidencias parciales entre nombres de componentes y documentos (ej: `CDS111` en `CDS111_manual.pdf`).
- **Importar/Exportar datos:** Respalda todo tu catálogo en un archivo ZIP.
- **Compatibilidad multiplataforma:** Funciona en Windows y Linux (ajustes de DPI y fuentes incluidos).
- **Botones de donación** integrados (PayPal y Ko-fi) para apoyar el desarrollo.

---

## 📦 Requisitos

- **Python 3.7 o superior**
- **PyQt5** (instalado automáticamente con `pip`)
- **Sistema operativo:** Windows 10/11 o Linux (distribuciones con entorno gráfico)

---

## 🚀 Instalación

### Opción 1: Ejecutar el código fuente

1. Clona o descarga este repositorio:
   ```bash
   git clone https://github.com/Chelo-C/Electrocatalog.git
   cd Electrocatalog
   ```

2. Instala las dependencias:
   ```bash
   pip install PyQt5
   ```

3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

### Opción 2: Ejecutable precompilado (próximamente)

Se planea distribuir un ejecutable empaquetado con PyInstaller para que no necesites instalar Python.

---

## 🖥️ Uso rápido

Al abrir la aplicación verás dos pestañas principales:

### Pestaña "Componentes"
- Agrega un nuevo componente con el botón correspondiente.
- Busca, filtra o elimina componentes de tu lista.
- Al hacer clic derecho (o selectionar), puedes ver/locs documents vinculados.

### Pestaña "Datasheets y Manuales"
- Sube o gestiona tus documentos (PDFs, manuales, hojas de datos).
- Asócialos con los componentes que correspondan.

### Menú "Vincular" -> "Buscar Vínculos"
- El sistema escanea automáticamente tu catálogo y sugiere coincidencias entre componentes y documentos.
- Marca las que desee y haz clic en "Vincular Seleccionados".

### Menú "Archivo"
- **Exportar Datos:** Crea un respaldo ZIP de todo tu catálogo.
- **Importar Datos:** Restaura un respaldo previo.
- **Actualiza Datos:** Recarga la información en caso de cambios externos.

---

## 🛠️ Desarrollo y Contribuir

Si quieres mejorar ElectroCatalog, sigues estos pasos:

1. Haz un fork del proyecto.
2. Crea una rama para tu feature: `git checkout -b mi-nueva-funcionalidad`
3. Commit tus cambios: `git commit -m "Añadir: descripción de la feature"`
4. Push a la rama: `git push origin mi-nueva-funcionalidad`
5. Abre un Pull Request describiendo los cambios.

**Estándares de código:**
- Usa PEP 8 para Python.
- Mantén la interfaz coherente con el tema oscuro existente.
- Añade comentarios en español o inglés (el código base está en español).

---

## ❤️ Apoyar el proyecto

Si ElectroCatalog te ayuda a organizar tu taller o a encontrar ese datasheet que salvó tu proyecto, considera invitarme un café. Tu apoyo me motiva a seguir corrigiendo errores y añadiendo nuevas funcionalidades.

- **PayPal:** [paypal.me/electrocatalog](https://paypal.me/electrocatalog)
- **Ko-fi:** [ko-fi.com/electrocatalog](https://ko-fi.com/electrocatalog)

---

## 📄 Licencia

**ElectroCatalog** es software libre y se distribuye bajo los términos de la **GNU General Public License v3.0 o posterior (GPL-3.0-or-later)**.

Puedes utilizarlo, estudiarlo, modificarlo y compartirlo libremente, siempre respetando las condiciones de esta licencia:
- Las versiones modificadas que se distribuyan deberán conservar estas mismas libertades y proporcionar el código fuente correspondiente.
- El uso comercial está permitido bajo los términos de la GPL.
- Las donaciones son voluntarias y siempre serán bienvenidas.

Consulta el archivo [LICENSE](LICENSE) para conocer los términos completos.

---

**Desarrollado por Chelo** ⚡