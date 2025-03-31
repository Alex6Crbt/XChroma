import sys
from PyQt6.QtWidgets import QApplication
from XChroma.app import MainWindow
from sequence import Sequence

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Sequence)
    window.show()
    sys.exit(app.exec())
