# ui/util/resize_window.py

# ---Centers a QWidget on the screen


from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget


def size_and_center_window(window: QWidget, width_percent: float, height_percent: float) -> None:
    screen_geo = QApplication.primaryScreen().availableGeometry()

    new_w = int(screen_geo.width() * width_percent)
    new_h = int(screen_geo.height() * height_percent)
    window.resize(new_w, new_h)

    left_margin = int(screen_geo.width() * 0.05)
    x = screen_geo.left() + left_margin
    y = screen_geo.top() + (screen_geo.height() - new_h) // 2
    window.move(QPoint(x, y))
