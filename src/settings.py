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
    QComboBox,
    QShortcut,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QRect
from overlay import OverlayWindow
from PyQt5.QtGui import QKeySequence
import json
from validator import preset_validator


class SettingsPanel(QMainWindow):
    def __init__(self, overlay_window: OverlayWindow):
        super().__init__()

        if overlay_window == None:
            self.overlay_window = None
        else:
            self.overlay_window = overlay_window

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Overlay Settings")
        self.setGeometry(50, 50, 400, 500)

        self.presets_name = "Untitiled"
        self.presets_file_path = None
        self.presets = self.init_presets()
        self.current_preset_idx = 0

        layout = QVBoxLayout()

        # Presets settings
        presets_layout = QVBoxLayout()
        presets_layout.addWidget(QLabel("Presets Name:"))
        self.current_presets_label = QLabel(self.presets_name)
        presets_layout.addWidget(self.current_presets_label)
        layout.addLayout(presets_layout)

        # Preset imports, saves and exports
        import_button = QPushButton("Import Presets")
        import_button.clicked.connect(self.import_presets)
        save_button = QPushButton("Save Presets")
        save_button.clicked.connect(self.save_presets)
        export_button = QPushButton("Export Presets")
        export_button.clicked.connect(self.export_presets)
        presets_layout.addWidget(import_button)
        presets_layout.addWidget(save_button)
        presets_layout.addWidget(export_button)

        # Preset Selection and Management
        preset_layout = QHBoxLayout()
        self.preset_combobox = QComboBox()
        self.preset_combobox.addItems(self.presets)
        self.preset_combobox.currentIndexChanged.connect(self.change_preset)
        preset_layout.addWidget(self.preset_combobox)
        layout.addLayout(preset_layout)

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

        self.toggle_size_adjustment_checkbox = QCheckBox("Toggle Size Adjustment Mode")
        self.toggle_size_adjustment_checkbox.setChecked(False)
        self.toggle_size_adjustment_checkbox.stateChanged.connect(
            self.update_overlay_window_flag
        )
        layout.addWidget(self.toggle_size_adjustment_checkbox)

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

        self.init_shortcut()

    def init_block_setting_panel(self, layout: QVBoxLayout):
        self.xywh_split = [["x", "y"], ["w", "h"]]
        self.xywh_range = {
            "x": 3840,
            "y": 2160,
            "w": 3840,
            "h": 2160,
        }
        self.xywh_name = {"x": "X", "y": "Y", "w": "Width", "h": "Height"}

        for first_idx, first in enumerate(["Position", "Size"]):
            # Block Controls
            layout.addWidget(QLabel("Block {}:".format(first)))
            # Absolute Mode Toggle
            mode_layout = QHBoxLayout()
            absolute_checkbox = QCheckBox("Use Absolute {}".format(first))
            absolute_checkbox.setChecked(True)  # Default to absolute mode
            absolute_checkbox.stateChanged.connect(
                lambda state, idx=first_idx: self.toggle_mode(state, idx)
            )
            mode_layout.addWidget(absolute_checkbox)
            self.absolute_checkbox[first_idx] = absolute_checkbox
            layout.addLayout(mode_layout)

            for second in self.xywh_split[first_idx]:
                block_layout = QHBoxLayout()
                block_layout.addWidget(
                    QLabel("{} {}:".format(self.xywh_name[second], first))
                )
                spinbox = QDoubleSpinBox()
                spinbox.setDecimals(2)
                spinbox.setRange(0, self.xywh_range[second])  # Supports up to 4K width
                spinbox.valueChanged.connect(
                    lambda _, xywh=second: self.update_block(xywh)
                )
                block_layout.addWidget(spinbox)
                self.block_spinbox[second] = spinbox
                self.unit_labels[second] = QLabel("px")
                block_layout.addWidget(self.unit_labels[second])
                layout.addLayout(block_layout)

    def init_presets(self):
        if self.overlay_window == None:
            return [
                {
                    "preset_name": "default",
                    "alpha": 150,
                    "x": 100,
                    "y": 100,
                    "w": 400,
                    "h": 400,
                    "xy_abs": True,
                    "wh_abs": True,
                }
            ]
        else:
            screen = self.overlay_window.screen().geometry()
            return [
                {
                    "preset_name": "default",
                    "alpha": 150,
                    "x": screen.width() // 4,
                    "y": screen.height() // 4,
                    "w": screen.width() // 2,
                    "h": screen.height() // 2,
                    "xy_abs": True,
                    "wh_abs": True,
                }
            ]

    def init_block_value(self):
        self.xywh = ["x", "y", "w", "h"]

        if self.overlay_window == None:
            return
        screen = self.overlay_window.primary_screen.geometry()
        self.block_xywh_value = {
            "x": screen.width() // 4,
            "y": screen.height() // 4,
            "w": screen.width() // 2,
            "h": screen.height() // 2,
        }

        # update every pair of values
        for i in self.xywh:
            self.block_spinbox[i].setValue(self.block_xywh_value[i])

    def init_shortcut(self):
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(
            self.close_application
        )

    def is_pos(self, xywh: str):
        return xywh == "x" or xywh == "y"

    def is_pos_split_idx(self, xywh: str):
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

    def import_presets(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Presets",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options,
        )
        if file_path:
            self.presets_file_path = file_path
            try:
                with open(file_path, "r") as file:
                    imported_data = json.load(file)
                    validate_result = preset_validator(imported_data)
                    if validate_result:
                        self.presets_name = imported_data["presets_name"]
                        self.presets = imported_data["presets"]
                        self.update_preset_combobox()
                        QMessageBox.information(
                            self,
                            "Import Successful",
                            "Presets have been imported successfully.",
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Import Failed",
                            "The selected file does not contain valid presets.",
                        )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"An error occurred while importing presets: {e}"
                )

    def save_presets(self):
        if self.presets_file_path:
            try:
                with open(self.presets_file_path, "w") as file:
                    json.dump(self.presets, file, indent=4)
                QMessageBox.information(
                    self,
                    "Save Successful",
                    "Presets have been saved successfully.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"An error occurred while saving presets: {e}"
                )
        else:
            self.export_presets()

    def export_presets(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Presets",
            "presets.json",
            "JSON Files (*.json);;All Files (*)",
            options=options,
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    json.dump(self.presets, file, indent=4)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    "Presets have been exported successfully.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"An error occurred while exporting presets: {e}"
                )

    def change_preset(self, index):
        if not self.overlay_window:
            return

        self.current_preset_idx = index
        self.update_preset_combobox()

    def update_preset_combobox(self):
        if self.presets:
            presets = self.presets[self.current_preset_idx]

            # Update abs/rel mode
            self.absolute_checkbox[0] = presets["xy_abs"]
            self.absolute_checkbox[1] = presets["wh_abs"]

            # Update block value
            self.block_xywh_value["x"] = presets["x"]
            self.block_xywh_value["y"] = presets["y"]
            self.block_xywh_value["w"] = presets["w"]
            self.block_xywh_value["h"] = presets["h"]
            self.update_xywh_spinbox_all()

            # Update transparency
            self.update_alpha(presets["alpha"])

            # Update color
            # self.pick_color()

            if self.overlay_window:
                self.overlay_window.update()

    def toggle_mode(self, state, split_idx):
        if not self.overlay_window:
            return

        is_absolute = state == Qt.Checked

        pair = self.get_screen_pairs()

        if is_absolute:
            # Switch to absolute mode
            for i in self.xywh_split[split_idx]:
                self.block_spinbox[i].setRange(0, self.xywh_range[i])
                self.block_spinbox[i].setValue(self.block_xywh_value[i])
                self.unit_labels[i].setText("px")
        else:
            # Switch to relative mode
            for i in self.xywh_split[split_idx]:
                percentage = (self.block_xywh_value[i] / pair[i]) * 100
                self.block_spinbox[i].setRange(0, 100)
                self.block_spinbox[i].setValue(percentage)
                self.unit_labels[i].setText("%")

    def update_block(self, xywh):
        if not self.overlay_window:
            return
        pair = self.get_screen_pairs()
        split_idx = self.is_pos_split_idx(xywh)

        if self.absolute_checkbox[split_idx].isChecked():
            self.block_xywh_value[xywh] = self.block_spinbox[xywh].value()
        else:
            self.block_xywh_value[xywh] = pair[xywh] * (
                self.block_spinbox[xywh].value() / 100
            )

        new_rect = QRect(
            self.block_xywh_value["x"],
            self.block_xywh_value["y"],
            self.block_xywh_value["w"],
            self.block_xywh_value["h"],
        )
        self.overlay_window.focus_block = new_rect
        self.overlay_window.update()

    def update_xywh_spinbox_all(self):
        if not self.overlay_window:
            return
        pair = self.get_screen_pairs()
        for split_idx in range(2):
            for i in self.xywh_split[split_idx]:
                if self.absolute_checkbox[split_idx].isChecked():
                    self.block_spinbox[i].setValue(self.block_xywh_value[i])
                else:
                    self.block_spinbox[i].setValue(
                        self.block_xywh_value[i] / pair[i] * 100
                    )

    def update_overlay_window_flag(self):
        if not self.overlay_window:
            return

        # Save current window position and size
        current_pos = self.overlay_window.pos()
        current_rect = self.overlay_window.geometry()

        # Start with default
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow

        # Add flags based on checkbox states
        if not self.toggle_size_adjustment_checkbox.isChecked():
            flags |= Qt.WindowTransparentForInput

        # Update window flags
        self.overlay_window.setWindowFlags(flags)

        # Restore window position and show
        self.overlay_window.setGeometry(current_rect)
        self.overlay_window.show()

        # Raise the level of setting panel to prevent blocking
        self.raise_()

    def update_alpha(self, value):
        self.presets[self.current_preset_idx]['alpha'] = value
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
            self.presets[self.current_preset_idx]['color'] = color
            if color.isValid():
                color.setAlpha(self.presets[self.current_preset_idx]['alpha'])
                self.overlay_window.overlay_color = color
                self.overlay_window.update()

    def close_application(self):
        if self.overlay_window:
            self.overlay_window.close()
        self.close()
