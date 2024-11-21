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
    QDoubleSpinBox,
)
from PyQt5.QtCore import Qt, QRect
from overlay import OverlayWindow
from functools import partial


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

        self.block_spinbox = {}
        self.unit_labels = {}
        self.absolute_checkbox = [None, None]

        self.init_block_setting_panel(layout)
        self.init_block_value()

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

    def init_block_setting_panel(self, layout: QVBoxLayout):
        self.xywh_split = [["x", "y"], ["w", "h"]]
        self.xywh_range = {
            "x": 3840,
            "y": 2160,
            "w": 3840,
            "h": 2160,
        }

        toggle_functions = [
            partial(lambda state, idx=idx: self.toggle_mode(state, idx))
            for idx in range(2)
        ]

        for first_idx, first in enumerate(["Position", "Size"]):
            # Block Controls
            layout.addWidget(QLabel("Block {}:".format(first)))
            # Absolute Mode Toggle
            mode_layout = QHBoxLayout()
            absolute_checkbox = QCheckBox("Use Absolute {}".format(first))
            absolute_checkbox.setChecked(True)  # Default to absolute mode
            absolute_checkbox.stateChanged.connect(toggle_functions[first_idx])
            mode_layout.addWidget(absolute_checkbox)
            self.absolute_checkbox[first_idx] = absolute_checkbox
            layout.addLayout(mode_layout)

            for second in self.xywh_split[first_idx]:
                block_layout = QHBoxLayout()
                block_layout.addWidget(
                    QLabel("{} {}:".format(second.capitalize(), first))
                )
                spinbox = QDoubleSpinBox()
                spinbox.setDecimals(2)
                spinbox.setRange(0, self.xywh_range[second])  # Supports up to 4K width
                spinbox.valueChanged.connect(lambda: self.update_block(second))
                self.block_spinbox[second] = spinbox
                block_layout.addWidget(spinbox)
                self.unit_labels[second] = QLabel("px")
                block_layout.addWidget(self.unit_labels[second])
                layout.addLayout(block_layout)

    def init_block_value(self):
        self.xywh = ["x", "y", "w", "h"]

        if self.overlay_window == None:
            return
        screen = self.overlay_window.primary_screen.geometry()
        self._block = {
            "x": screen.width() // 4,
            "y": screen.height() // 4,
            "w": screen.width() // 2,
            "h": screen.height() // 2,
        }

        # update every pair of values
        for i in self.xywh:
            self.block_spinbox[i].setValue(self._block[i])

    def is_pos(self, xywh: str):
        return xywh == "x" or xywh == "y"

    def is_pos_idx(self, xywh: str):
        if xywh == "x" or xywh == "y":
            return 0
        return 1

    def get_screen_pairs(self):
        screen = self.overlay_window.primary_screen.geometry()
        pair = {
            "x": screen.width(),
            "y": screen.height(),
            "w": screen.width(),
            "h": screen.height(),
        }
        return pair

    def toggle_mode(self, state, split_idx):
        if self.overlay_window == None:
            return

        is_absolute = state == Qt.Checked

        pair = self.get_screen_pairs()

        if is_absolute:
            # Switch to absolute mode
            for i in self.xywh_split[split_idx]:
                self.block_spinbox[i].setRange(0, self.xywh_range[i])
                self.block_spinbox[i].setValue(self._block[i])
                self.unit_labels[i].setText("px")
        else:
            # Switch to relative mode
            for i in self.xywh_split[split_idx]:
                percentage = (self._block[i] / pair[i]) * 100
                self.block_spinbox[i].setRange(0, 100)
                self.block_spinbox[i].setValue(percentage)
                self.unit_labels[i].setText("%")

    def update_block(self, xywh):
        if not self.overlay_window:
            return
        screen = self.overlay_window.primary_screen.geometry()
        pair = {
            "x": screen.width(),
            "y": screen.height(),
            "w": screen.width(),
            "h": screen.height(),
        }
        split_idx = self.is_pos_idx(xywh)

        if self.absolute_checkbox[split_idx].isChecked():
            self._block[xywh] = self.block_spinbox[xywh].value()
        else:
            self._block[xywh] = pair[xywh] * (self.block_spinbox[xywh].value() / 100)

        new_rect = QRect(
            self._block["x"], self._block["y"], self._block["w"], self._block["h"]
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