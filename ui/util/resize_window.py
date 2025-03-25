# ui/util/resize_window.py

# ---Centers a QWidget on the screen


from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget


def size_and_center_window(window: QWidget, width_percent: float, height_percent: float) -> None:
    # ---Center Window on Screen
    screen = QApplication.primaryScreen().size()
    window.setGeometry(0, 0, int(screen.width() * width_percent), int(screen.height() * height_percent))

    window.move(
        QApplication.primaryScreen().availableGeometry().center() - window.rect().center(),
    )