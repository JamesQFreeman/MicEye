import json

import qdarkstyle
from PyQt5.QtWidgets import (QApplication, QInputDialog, QMessageBox)
from PyQt5.QtGui import QFont
from LoadingWindow import LoadingWindow
from MainWindow import MainWindow
from utils.gazeUtils import refresh
from utils.qtUtils import moveToCenter

helloMessage = '''
This is MIC EYE. 

Look at images, and classify them by typing 0,1,2,3,4,5... on the keyboard, next image will show up.
You can stop any time and the result will be automatically saved in background.

Yours,
MIC EYE-2.0 Beta
'''

config = json.load(open('config.json'))
loadingWait: int = config["loading wait"]
font: QFont = QFont(config["font"], 16)
font.setBold(True)
darkMode = config["dark mode"]
logDir = config["save log to"]

if __name__ == "__main__":
    app = QApplication([])
    startWindow = LoadingWindow(waitTime=loadingWait)
    moveToCenter(startWindow)
    startWindow.exec_()
    main = MainWindow(imageDimension=2)
    if darkMode:
        app.setStyleSheet(qdarkstyle.load_stylesheet())
    moveToCenter(main)
    volunteerName, _ = QInputDialog.getText(main, "Name Input", "Please type your name:")
    helloBox = QMessageBox()
    helloBox.setWindowTitle("To user")

    helloBox.setFont(font)
    helloBox.setText(f"Hi! {volunteerName},\n" + helloMessage)
    moveToCenter(helloBox)
    helloBox.exec_()
    refresh()
    main.setLogSystem(volunteerName, logDir)
    main.show()
    moveToCenter(main)
    app.exec_()
