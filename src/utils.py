from PyQt5.QtGui import QColor


def color_to_hex(color: QColor):
    """Convert QColor to hex string"""
    return f"#{color.red():02x}{color.green():02x}{color.blue():02x}"


def hex_to_color(hex: str):
    """Convert hex string to QColor"""
    # Remove #
    hex = hex.lstrip("#")
    # Convert hex to RGB
    rgb = tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
    # Create QColor
    return QColor(*rgb, 0)
