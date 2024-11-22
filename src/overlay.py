from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
)
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QRect


class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Default flag
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.SubWindow
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Get primary screen
        self.primary_screen = QApplication.primaryScreen()
        screen_geometry = self.primary_screen.geometry()
        self.setGeometry(screen_geometry)

        # Block init
        self.focus_block = QRect(0, 0, 0, 0)

        # Overlay visual settings
        self.overlay_color = QColor(0, 0, 0, 150)
        self.show_focus_block = True

    def paintEvent(self, event):
        if not self.show_focus_block:
            return

        painter = QPainter(self)
        painter.setBrush(self.overlay_color)
        painter.setPen(Qt.NoPen)

        # Draw the overlay outside the focus block
        painter.drawRect(self.rect())
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.focus_block, Qt.transparent)
