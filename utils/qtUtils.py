from PyQt5.QtWidgets import (QApplication, QWidget, QGroupBox, QInputDialog, QDialog, QPushButton,
                             QLabel, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLineEdit)


def moveToCenter(widget: QWidget):
    qtRectangle = widget.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    widget.move(qtRectangle.topLeft())
