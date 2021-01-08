import os
os.environ['QT_API'] = 'pyside2'
import sys
from pathlib import Path
 
from qtpy.QtWidgets import QApplication, QMainWindow 
from qtpy.QtGui import QIcon


class MiVentana(QMainWindow): 
    def __init__(self):
        super().__init__()
        self._create_ui()
 
    def _create_ui(self):
        self.resize(500, 300)
        self.move(0, 0)
        self.setWindowTitle('Hola, QMainWindow')
        ruta_icono = Path('.', 'imgs', 'pybofractal.png')
        self.setWindowIcon(QIcon(str(ruta_icono)))
        self.show()
 
if __name__ == '__main__':
 
    app = QApplication(sys.argv)
    w = MiVentana()
    sys.exit(app.exec_())