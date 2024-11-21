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
)
from PyQt5.QtCore import Qt, QRect
from overlay import OverlayWindow


class SettingsPanel(QMainWindow):
    def __init__(self, overlay_window: OverlayWindow):
        super().__init__()

        if overlay_window == None:
            self.overlay_window = None
        else:
            self.overlay_window = overlay_window

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
        layout.addWidget(QLabel("Block Position:"))

        # Size and Position Mode Toggle
        pos_mode_layout = QHBoxLayout()
        self.absolute_pos_checkbox = QCheckBox("Use Absolute Position")
        self.absolute_pos_checkbox.setChecked(True)  # Default to absolute mode
        self.absolute_pos_checkbox.stateChanged.connect(self.toggle_pos_mode)
        pos_mode_layout.addWidget(self.absolute_pos_checkbox)
        layout.addLayout(pos_mode_layout)

        # X Position
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Position:"))
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 3840)  # Supports up to 4K width
        self.x_spinbox.valueChanged.connect(lambda: self.update_block("x"))
        x_layout.addWidget(self.x_spinbox)
        self.x_unit_label = QLabel("px")
        x_layout.addWidget(self.x_unit_label)
        layout.addLayout(x_layout)

        # Y Position
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Position:"))
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 2160)  # Supports up to 4K height
        self.y_spinbox.valueChanged.connect(lambda: self.update_block("y"))
        y_layout.addWidget(self.y_spinbox)
        self.y_unit_label = QLabel("px")
        y_layout.addWidget(self.y_unit_label)
        layout.addLayout(y_layout)

        # Block Size Controls
        layout.addWidget(QLabel("Block Size:"))

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
        self.width_spinbox.setRange(0, 3840)
        self.width_spinbox.valueChanged.connect(lambda: self.update_block("w"))
        width_layout.addWidget(self.width_spinbox)
        self.width_unit_label = QLabel("px")
        width_layout.addWidget(self.width_unit_label)
        layout.addLayout(width_layout)

        # Height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(0, 2160)
        self.height_spinbox.valueChanged.connect(lambda: self.update_block("h"))
        height_layout.addWidget(self.height_spinbox)
        self.height_unit_label = QLabel("px")
        height_layout.addWidget(self.height_unit_label)
        layout.addLayout(height_layout)

        self.init_block()

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

    def init_block(self):
        if self.overlay_window == None:
            return

        screen_geometry = self.overlay_window.primary_screen.geometry()

        self._block = {
            "x": screen_geometry.width() // 4,
            "y": screen_geometry.height() // 4,
            "h": screen_geometry.width() // 2,
            "w": screen_geometry.height() // 2,
        }

        self.x_spinbox.setValue(self._block["x"])
        self.y_spinbox.setValue(self._block["y"])
        self.width_spinbox.setValue(self._block["w"])
        self.height_spinbox.setValue(self._block["h"])

    def toggle_pos_mode(self, state):
        if self.overlay_window == None:
            return

        is_absolute = state == Qt.Checked
        screen = self.overlay_window.primary_screen.geometry()
        # current_rect = self.overlay_window.focus_block

        if is_absolute:
            # Switch to absolute mode
            # Position
            self.x_spinbox.setRange(0, 3840)
            self.y_spinbox.setRange(0, 2160)
            self.x_spinbox.setValue(self._block["x"])
            self.y_spinbox.setValue(self._block["y"])
            self.x_unit_label.setText("px")
            self.y_unit_label.setText("px")
        else:
            # Switch to relative mode
            # Position
            x_percentage = (self._block["x"] / screen.width()) * 100
            y_percentage = (self._block["y"] / screen.height()) * 100
            self.x_spinbox.setRange(0, 100)
            self.y_spinbox.setRange(0, 100)
            self.x_spinbox.setValue(x_percentage)
            self.y_spinbox.setValue(y_percentage)
            self.x_unit_label.setText("%")
            self.y_unit_label.setText("%")

    def toggle_size_mode(self, state):
        if self.overlay_window == None:
            return

        is_absolute = state == Qt.Checked

        screen = self.overlay_window.primary_screen.geometry()

        if is_absolute:
            # Switch to absolute size mode
            self.width_spinbox.setRange(0, 3840)
            self.height_spinbox.setRange(0, 2160)
            self.width_spinbox.setValue(self._block["w"])
            self.height_spinbox.setValue(self._block["h"])
            self.width_unit_label.setText("px")
            self.height_unit_label.setText("px")
        else:
            # Switch to relative size mode
            # Convert to percentage
            width_percentage = (self._block["w"] / screen.width()) * 100
            height_percentage = (self._block["h"] / screen.height()) * 100

            self.width_spinbox.setRange(0, 100)
            self.height_spinbox.setRange(0, 100)
            self.width_spinbox.setValue(width_percentage)
            self.height_spinbox.setValue(height_percentage)
            self.width_unit_label.setText("%")
            self.height_unit_label.setText("%")

    def update_block(self, val_name):
        if not self.overlay_window:
            return
        screen = self.overlay_window.primary_screen.geometry()

        val_name_table = {
            "x": {
                "box": self.x_spinbox,
                "rel": screen.width(),
                "is_abs": self.absolute_pos_checkbox.isChecked(),
            },
            "y": {
                "box": self.y_spinbox,
                "rel": screen.height(),
                "is_abs": self.absolute_pos_checkbox.isChecked(),
            },
            "w": {
                "box": self.width_spinbox,
                "rel": screen.width(),
                "is_abs": self.absolute_size_checkbox.isChecked(),
            },
            "h": {
                "box": self.height_spinbox,
                "rel": screen.height(),
                "is_abs": self.absolute_size_checkbox.isChecked(),
            },
        }

        if val_name in val_name_table:
            properties = val_name_table[val_name]
            if properties["is_abs"]:
                self._block[val_name] = properties["box"].value()
            else:
                self._block[val_name] = properties["rel"] * (
                    properties["box"].value() / 100
                )

        new_rect = QRect(
            self._block["x"], self._block["y"], self._block["h"], self._block["w"]
        )
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
