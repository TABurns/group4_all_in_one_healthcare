# ui/main_window.py

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)


class MainWindow(QMainWindow):
    def __init__(self, root: QApplication, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.root = root # ---Main Application

        self.setObjectName("MainWindow")
        self.setWindowTitle("Smart Healthcare Systems")



