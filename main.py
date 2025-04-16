import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
)

from ui.config.logger_config import logger
from ui.config.paths import STYLES
from ui.main_window import MainWindow
from ui.util.resize_window import size_and_center_window
from ui.working_area import WorkingArea


class RootApp(QApplication):
    def __init__(self) -> None:
        super().__init__([])  # --Passes cmds to application

        self.working_area = None  # ---Window to stack sub windows

    def check_setup(self) -> bool:
        from ui.config.paths import SETUP_DB

        return SETUP_DB.exists()

    def run_setup(self) -> bool:
        from ui.setup_page import SetupPage

        setup_dialog = SetupPage()
        return setup_dialog.exec() == QDialogButtonBox.StandardButton.Ok

    # --------------------------------------------------------
    # --Apply css styles
    # --------------------------------------------------------
    def _load_stylesheet(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as err:
            logger.error(f"Failed to load stylesheet from {path}: {err}")
            return ""

    #    def _load_secondary_windows(self) -> None:

    def _boot_app(self) -> None:

        # ---Apply stylesheet early so that widgets render properly
        self.setStyleSheet(self._load_stylesheet(STYLES))

        if not self.check_setup() and not self.run_setup():
            sys.exit(0)

        self.working_area = WorkingArea()

        main_window = MainWindow(self)



        # ---Delay showing the main window until after guide_window is fully displayed.
        QTimer.singleShot(10, main_window.show)
        size_and_center_window(main_window, 0.85, 0.75)

        self.processEvents()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = RootApp()
    app._boot_app()
