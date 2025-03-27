# ui/main_window.py


from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import ROOT_BACKGROUND

if TYPE_CHECKING:
    from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self, root: QApplication, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.root = root  # ---Main Application

        self.working_area = QStackedWidget(objectName="WorkingArea")  # ---Window to display sub windows.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setObjectName("MainWindow")
        self.setWindowTitle("Good Doctors Medical Group")

        root_widget = QWidget(self, objectName="root_widget")  # ---Main widget to build on


        main_layout = QHBoxLayout(root_widget)
        self.setCentralWidget(root_widget)


        # ---Widget for sidebar btns.
        sidebar_widget: QWidget = QWidget(self, objectName="SideBarWidget")
        sidebar_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sidebar_layout: QVBoxLayout = QVBoxLayout(sidebar_widget)

        # ---Add sub window btns to sidebar
        self._add_buttons(sidebar_layout)

        # ---Footer
        foot = QLabel("© 2025 Smart Healthcare Systems", self, objectName="Footer")
        sidebar_layout.addWidget(foot)

        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.working_area, 5)

    # ******************************************************************************************
    #  / Handle Buttons
    # ******************************************************************************************

    def _build_button(self, btn_label: str, function: callable) -> QPushButton:
        btn: QPushButton = QPushButton(f"{btn_label}", self, objectName="RootBTN")
        btn.clicked.connect(function)
        return btn

    # --------------------------------------

    def _add_buttons(self, sidebar_layout: QVBoxLayout) -> None:
        # ---Add sidebar buttons to the layout with functions
        buttons_info: list[tuple[Path, str, callable]] = [
            ("Scan Reels", self._do_something),
            ("Search Reels", self._do_something),
            ("Yam-Server", self._do_something),
        ]

        for btn_label, function in buttons_info:
            sidebar_layout.addWidget(self._build_button(btn_label, function))
        sidebar_layout.addStretch()

    def _do_something(self) -> None:
        print("btn clicked...")
