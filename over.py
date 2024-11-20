import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QColorDialog,
    QWidget,
    QLabel,
    QCheckBox,
    QHBoxLayout,
    QSpinBox,
    QMessageBox,
)
from PyQt5.QtGui import QColor, QPainter, QScreen
from PyQt5.QtCore import Qt, QRect


class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Enhanced window configuration
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

        # Block settings with more flexible positioning
        self.focus_block = QRect(
            screen_geometry.width() // 4,  # Default X position
            screen_geometry.height() // 4,  # Default Y position
            screen_geometry.width() // 2,  # Default Width
            screen_geometry.height() // 2,  # Default Height
        )

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


class SettingsPanel(QMainWindow):
    def __init__(self):
        super().__init__()

        self.overlay_window = None
        self.setWindowTitle("Overlay Settings")
        self.setGeometry(50, 50, 400, 500)

        layout = QVBoxLayout()

        # Transparency Slider
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(QLabel("Overlay Transparency:"))
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(255)
        self.alpha_slider.setValue(150)
        self.alpha_slider.valueChanged.connect(self.update_alpha)
        transparency_layout.addWidget(self.alpha_slider)
        layout.addLayout(transparency_layout)

        # Block Position Controls
        position_group = QLabel("Block Position:")
        layout.addWidget(position_group)

        # X Position
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Position:"))
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 3840)  # Supports up to 4K width
        self.x_spinbox.valueChanged.connect(self.update_block_position)
        x_layout.addWidget(self.x_spinbox)
        layout.addLayout(x_layout)

        # Y Position
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Position:"))
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 2160)  # Supports up to 4K height
        self.y_spinbox.valueChanged.connect(self.update_block_position)
        y_layout.addWidget(self.y_spinbox)
        layout.addLayout(y_layout)

        # Block Size Controls
        size_group = QLabel("Block Size:")
        layout.addWidget(size_group)

        # Size Mode Toggle
        size_mode_layout = QHBoxLayout()
        self.absolute_size_checkbox = QCheckBox("Use Absolute Size")
        self.absolute_size_checkbox.setChecked(True)  # Default to absolute size
        self.absolute_size_checkbox.stateChanged.connect(self.toggle_size_mode)
        size_mode_layout.addWidget(self.absolute_size_checkbox)
        layout.addLayout(size_mode_layout)

        # Width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, 3840)
        self.width_spinbox.valueChanged.connect(self.update_block_size)
        width_layout.addWidget(self.width_spinbox)
        self.width_unit_label = QLabel("px")
        width_layout.addWidget(self.width_unit_label)
        layout.addLayout(width_layout)

        # Height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(10, 2160)
        self.height_spinbox.valueChanged.connect(self.update_block_size)
        height_layout.addWidget(self.height_spinbox)
        self.height_unit_label = QLabel("px")
        height_layout.addWidget(self.height_unit_label)
        layout.addLayout(height_layout)

        # Show/Hide Focus Block
        self.show_focus_block_checkbox = QCheckBox("Show Focus Block")
        self.show_focus_block_checkbox.setChecked(True)
        self.show_focus_block_checkbox.stateChanged.connect(
            self.update_focus_block_visibility
        )
        layout.addWidget(self.show_focus_block_checkbox)

        # Color selection
        color_button = QPushButton("Select Overlay Color")
        color_button.clicked.connect(self.pick_color)
        layout.addWidget(color_button)

        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close_application)
        layout.addWidget(exit_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def toggle_size_mode(self, state):
        is_absolute = state == Qt.Checked

        if is_absolute:
            # Switch to absolute size mode
            self.width_spinbox.setRange(10, 3840)
            self.height_spinbox.setRange(10, 2160)
            self.width_spinbox.setValue(self.overlay_window.focus_block.width())
            self.height_spinbox.setValue(self.overlay_window.focus_block.height())
            self.width_unit_label.setText("px")
            self.height_unit_label.setText("px")
        else:
            # Switch to relative size mode
            screen = QApplication.primaryScreen().geometry()
            current_width = self.overlay_window.focus_block.width()
            current_height = self.overlay_window.focus_block.height()

            # Convert to percentage
            width_percentage = int((current_width / screen.width()) * 100)
            height_percentage = int((current_height / screen.height()) * 100)

            self.width_spinbox.setRange(1, 100)
            self.height_spinbox.setRange(1, 100)
            self.width_spinbox.setValue(width_percentage)
            self.height_spinbox.setValue(height_percentage)
            self.width_unit_label.setText("%")
            self.height_unit_label.setText("%")

    def update_block_position(self):
        if not self.overlay_window:
            return

        x = self.x_spinbox.value()
        y = self.y_spinbox.value()
        current_rect = self.overlay_window.focus_block

        new_rect = QRect(x, y, current_rect.width(), current_rect.height())

        self.overlay_window.focus_block = new_rect
        self.overlay_window.update()

    def update_block_size(self):
        if not self.overlay_window:
            return

        screen = QApplication.primaryScreen().geometry()

        if self.absolute_size_checkbox.isChecked():
            # Absolute size mode
            width = self.width_spinbox.value()
            height = self.height_spinbox.value()
        else:
            # Relative size mode
            width = int(screen.width() * (self.width_spinbox.value() / 100))
            height = int(screen.height() * (self.height_spinbox.value() / 100))

        current_rect = self.overlay_window.focus_block

        new_rect = QRect(current_rect.x(), current_rect.y(), width, height)

        self.overlay_window.focus_block = new_rect
        self.overlay_window.update()

    def update_alpha(self, value):
        if self.overlay_window:
            self.overlay_window.overlay_color.setAlpha(value)
            self.overlay_window.update()

    def update_focus_block_visibility(self, state):
        if self.overlay_window:
            self.overlay_window.show_focus_block = state == Qt.Checked
            self.overlay_window.update()

    def pick_color(self):
        if self.overlay_window:
            color = QColorDialog.getColor(self.overlay_window.overlay_color)
            if color.isValid():
                self.overlay_window.overlay_color = color
                self.overlay_window.update()

    def close_application(self):
        if self.overlay_window:
            self.overlay_window.close()
        self.close()


def main():
    app = QApplication(sys.argv)

    # Create overlay window
    overlay_window = OverlayWindow()
    overlay_window.show()

    # Create settings panel
    settings_panel = SettingsPanel()
    settings_panel.overlay_window = overlay_window
    settings_panel.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
