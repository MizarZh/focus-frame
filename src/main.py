import sys
from PyQt5.QtWidgets import (
    QApplication,
)
from overlay import OverlayWindow
from settings import SettingsPanel


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
