from PyQt5 import QtCore
from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QDesktopWidget)

from utils.gazeUtils import eyeTrackerInit, getGazeCenter
from utils.imageUtils import createPixmapFromArray, imRead

import cv2
import numpy as np


def getPointInImage(absPoint, imPosition):
    x, y = [absPoint[0] - imPosition[0], absPoint[1] - imPosition[1]]
    x = max(min(imPosition[2], x), 0)
    y = max(min(imPosition[3], y), 0)
    return x, y


class BlurHole():
    def __init__(self, image):
        self.org = image
        self.blurred = cv2.GaussianBlur(self.org, (39, 39), 0)
        self.shape = self.org.shape

    def getHoleBlur(self, center, radius):
        mask = np.zeros(self.shape, dtype=np.uint8)
        cv2.circle(mask, center, radius, color=(1, 1, 1), thickness=-1)
        inversedMask = 1 - mask
        result = mask * self.org + inversedMask * self.blurred
        cv2.circle(result, center, radius, color=(230, 230, 230), thickness=3)
        return result


class LoadingWindow(QDialog):
    def __init__(self, waitTime: int = 5):
        super().__init__()
        eyeTrackerInit()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setWindowOpacity(0.9)
        self.imageLabel = QLabel()
        self.setStyleSheet("QDialog{margin-left: 0px; border-radius: 25px; background: white; color: #4A0C46;}")

        image = imRead('loadingWindow.jpg', int(QDesktopWidget().availableGeometry().height() / 1.5))
        self.blurHole = BlurHole(image)
        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel)
        self.setLayout(layout)
        self.refreshTimer = QtCore.QTimer(self)
        self.refreshTimer.start(50)
        self.refreshTimer.timeout.connect(self.refresh)
        self.timer = QtCore.QTimer(self)
        self.timer.start(waitTime * 1000)
        self.timer.timeout.connect(self.myClose)

    def myClose(self):
        self.close()
        self.refreshTimer.stop()

    @property
    def imageGeometry(self):
        windowGeometry = self.frameGeometry()
        imageGeometry = self.imageLabel.frameGeometry()
        imageAbsGeometry = (windowGeometry.x() + imageGeometry.x(),
                            windowGeometry.y() + imageGeometry.y(),
                            imageGeometry.width(),
                            imageGeometry.height())
        return imageAbsGeometry

    def moveToCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def refresh(self):
        self.moveToCenter()
        gaze = getGazeCenter()
        if not gaze:
            return
        gaze = getPointInImage(gaze, self.imageGeometry)
        self.imageLabel.setPixmap(createPixmapFromArray(self.blurHole.getHoleBlur(center=gaze, radius=100)))
