from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QShortcut,
)
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QKeySequence


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

        self.block_selected = False
        self.resizing = False
        self.moving = False
        self.offset = None

        # QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(
        #     self.raiseSettingPanel
        # )

        self.adjust_tol = 50

    def paintEvent(self, event):
        if not self.show_focus_block:
            return

        painter = QPainter(self)
        painter.setBrush(self.overlay_color)
        painter.setPen(Qt.NoPen)

        # Draw the overlay outside the focus block
        painter.drawRect(self.rect())
        # painter.setCompositionMode(QPainter.CompositionMode_Clear) # no selection
        # painter.fillRect(self.focus_block, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOut)
        painter.drawRect(self.focus_block)
        # if alpha=0 then the focus block will be not selectable
        # set to 1
        painter.fillRect(self.focus_block, QColor(0, 0, 0, 1))

    def is_near_resize_corner(self, pos, tolerance=20):
        return (self.focus_block.bottomRight() - pos).manhattanLength() < tolerance

    def update_cursor(self, pos):
        corner = self.is_near_resize_corner(pos)
        edge = self.is_near_resize_edge(pos)

        if corner:
            if corner in ["top_left", "bottom_right"]:
                self.setCursor(Qt.SizeFDiagCursor)
            elif corner in ["top_right", "bottom_left"]:
                self.setCursor(Qt.SizeBDiagCursor)
        elif edge:
            if edge in ["top", "bottom"]:
                self.setCursor(Qt.SizeVerCursor)
            elif edge in ["left", "right"]:
                self.setCursor(Qt.SizeHorCursor)
        elif self.focus_block.contains(pos):
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            corner = self.is_near_resize_corner(event.pos())
            edge = self.is_near_resize_edge(event.pos())

            if corner:
                self.resizing = corner  # Store the corner being resized
            elif edge:
                self.resizing = edge  # Store the edge being resized
            elif self.focus_block.contains(event.pos()):
                self.moving = True
                self.offset = event.pos() - self.focus_block.topLeft()

    def mouseMoveEvent(self, event):
        self.update_cursor(event.pos())

        if isinstance(self.resizing, str):
            if "top" in self.resizing:
                new_top = min(
                    self.focus_block.bottom() - self.adjust_tol, max(0, event.y())
                )
                if new_top != self.focus_block.top():
                    self.focus_block.setTop(new_top)
            if "bottom" in self.resizing:
                new_bottom = max(
                    self.focus_block.top() + self.adjust_tol,
                    min(self.height(), event.y()),
                )
                if new_bottom != self.focus_block.bottom():
                    self.focus_block.setBottom(new_bottom)
            if "left" in self.resizing:
                new_left = min(
                    self.focus_block.right() - self.adjust_tol, max(0, event.x())
                )
                if new_left != self.focus_block.left():
                    self.focus_block.setLeft(new_left)
            if "right" in self.resizing:
                new_right = max(
                    self.focus_block.left() + self.adjust_tol,
                    min(self.width(), event.x()),
                )
                if new_right != self.focus_block.right():
                    self.focus_block.setRight(new_right)
        elif self.moving:
            new_pos = event.pos() - self.offset
            new_x = max(0, min(self.width() - self.focus_block.width(), new_pos.x()))
            new_y = max(0, min(self.height() - self.focus_block.height(), new_pos.y()))
            if new_x != self.focus_block.x() or new_y != self.focus_block.y():
                self.focus_block.moveTopLeft(QPoint(new_x, new_y))

        if hasattr(self, "settings") and self.settings:
            if not self.settings.isActiveWindow():
                self.settings.raise_()
            self.settings._block = {
                "x": self.focus_block.x(),
                "y": self.focus_block.y(),
                "w": self.focus_block.width(),
                "h": self.focus_block.height(),
            }
            self.settings.update_spinbox_from_overlay()
        self.update()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.moving = False
        self.setCursor(Qt.ArrowCursor)

    def is_near_resize_corner(self, pos, tolerance=20):
        corners = {
            "top_left": self.focus_block.topLeft(),
            "top_right": self.focus_block.topRight(),
            "bottom_left": self.focus_block.bottomLeft(),
            "bottom_right": self.focus_block.bottomRight(),
        }
        for key, corner in corners.items():
            if (corner - pos).manhattanLength() < tolerance:
                return key
        return None

    def is_near_resize_edge(self, pos, tolerance=20):
        edges = {
            "top": abs(pos.y() - self.focus_block.top()) < tolerance
            and self.focus_block.contains(
                QPoint(pos.x(), self.focus_block.center().y())
            ),
            "bottom": abs(pos.y() - self.focus_block.bottom()) < tolerance
            and self.focus_block.contains(
                QPoint(pos.x(), self.focus_block.center().y())
            ),
            "left": abs(pos.x() - self.focus_block.left()) < tolerance
            and self.focus_block.contains(
                QPoint(self.focus_block.center().x(), pos.y())
            ),
            "right": abs(pos.x() - self.focus_block.right()) < tolerance
            and self.focus_block.contains(
                QPoint(self.focus_block.center().x(), pos.y())
            ),
        }
        for key, hit in edges.items():
            if hit:
                return key
        return None

    def setSettingPanel(self, settings):
        self.settings = settings
