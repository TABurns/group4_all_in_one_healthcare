import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
)

from ui.config.logger_config import logger
from ui.config.paths import STYLES
from ui.main_window import MainWindow
from ui.util.resize_window import size_and_center_window


class RootApp(QApplication):
    def __init__(self) -> None:
        super().__init__([])  # --Passes cmds to application

    # main_window = None  # --Root window of application

    # --------------------------------------------------------
    # --Apply css styles
    # --------------------------------------------------------
    def _load_stylesheet(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as err:
            logger.error(f"Failed to load stylesheet from {path}: {err}")
            return ""

    def _boot_app(self) -> None:
        main_window = MainWindow(self)

        # ---Apply stylesheet early so that widgets render properly
        self.setStyleSheet(self._load_stylesheet(STYLES))

        # ---Delay showing the main window until after guide_window is fully displayed.
        QTimer.singleShot(10, main_window.show)
        size_and_center_window(main_window, 0.85, 0.75)

        self.processEvents()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = RootApp()
    app._boot_app()
