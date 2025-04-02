# working_area.py


from PySide6.QtWidgets import QSizePolicy, QStackedWidget, QWidget


class WorkingArea(QStackedWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WorkingArea")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
