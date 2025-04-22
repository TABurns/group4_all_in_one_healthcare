from collections.abc import Callable

from PySide6.QtGui import QBrush, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.new_patients import NewPatientWindow
from ui.working_area import WorkingArea


class MainWindow(QMainWindow):
    def __init__(self, root: QApplication, company_name: str, user_name: str, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.root = root  # ---Main Application
        self.working_area = WorkingArea(self)

        self.company_name = company_name
        self.user_name = user_name

        # ---Set window title and status bar
        self.setWindowTitle(self.company_name)
        sb = self.statusBar()
        sb.showMessage(f"Logged in as: {self.user_name}")
        sb.setStyleSheet("color: #3498db; font-weight: bold;")

        # ---Window to display sub windows.
        self.setObjectName("MainWindow")

        root_widget = QWidget(self)  # ---Main widget to build on
        root_widget.setObjectName("root_widget")

        main_layout = QHBoxLayout(root_widget)
        self.setCentralWidget(root_widget)

        # ---Set the background image
        pixmap = QPixmap("ui/resources/gooddr.png")
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

        # ---Widget for sidebar btns.
        sidebar_widget: QWidget = QWidget(self)
        sidebar_widget.setObjectName("SideBarWidget")
        sidebar_layout: QVBoxLayout = QVBoxLayout(sidebar_widget)

        # ---Add sub window btns to sidebar
        sidebar_layout.addStretch()  # ---push buttons to center of sidebar
        self._add_buttons(sidebar_layout)

        sidebar_layout.addStretch()  # ---Fill space between btns and footer

        # ---Footer
        foot = QLabel("© 2025 Smart Healthcare Systems", self)
        foot.setObjectName("Footer")
        sidebar_layout.addWidget(foot)

        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.working_area, 5)

    # ******************************************************************************************
    #  / Handle Buttons
    # ******************************************************************************************

    def _build_button(self, btn_label: str, function: Callable[[], None]) -> QPushButton:
        btn: QPushButton = QPushButton(f"{btn_label}", self)
        btn.setObjectName("RootBTN")
        btn.clicked.connect(function)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return btn

    # --------------------------------------

    def _add_buttons(self, sidebar_layout: QVBoxLayout) -> None:
        # ---Add sidebar buttons to the layout with functions
        buttons_info: list[tuple[str, Callable[[], None]]] = [
            ("New Patients", self._open_new_patient_portal),
            ("Schedule Appointment", self._do_something),
            ("Prescriptions", self._do_something),
        ]

        for btn_label, function in buttons_info:
            sidebar_layout.addWidget(self._build_button(btn_label, function))

    def _do_something(self) -> None:
        print("btn clicked...")

    def _open_new_patient_portal(self) -> None:
        self.new_patients_window = NewPatientWindow(self)
        self.working_area.addWidget(self.new_patients_window)
        self.working_area.setCurrentWidget(self.new_patients_window)
