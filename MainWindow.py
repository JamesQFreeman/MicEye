import glob
import time

import cv2
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QFont
from PyQt5.QtWidgets import (QWidget, QGroupBox, QPushButton, QFileDialog,
                             QLabel, QVBoxLayout, QHBoxLayout)
import random
import json
from utils.dataUtils import CsvLog
from utils.annoUtils import parseLabelmeXMl
from utils.gazeUtils import getGazeCenter, getGazeRaw
from utils.imageUtils import (createPixmapFromArray, imRead, crossHair, superimposeHeatmapToImage,
                              drawBBoxesOnImage, getImageFileSize, pointToHeatmap)


# TODO: 1. space+(0,1,2,3,4) for class label and move to next image     -> finished
#       2. get image position                                           -> finished
#       3. get the Eyetracker in                                        -> finished
#       4. get the photoshop-like opening                               -> finished
#       5. image resize                                                 -> finished
#       6. logging, all the data should be saved in csv.                -> finished
#       7. Add user hint                                                -> finished
#       8. Add bbox support                                             -> finished
#       9. Add folder selector                                          -> Replaced with config.json
#       10.Add Dark Mode                                                -> finished
#       11.add name text Box and where you want to save                 -> finished
#       12.setting in config.json                                       -> finished
#       13.Add 'Last image' button


def getPointInImage(absPoint, imPosition):
    x, y = [absPoint[0] - imPosition[0], absPoint[1] - imPosition[1]]
    x = max(min(imPosition[2], x), 0)
    y = max(min(imPosition[3], y), 0)
    return [x, y]


# The data we want to collect
class Data:
    def __init__(self, fileName: str):
        self.fileName = fileName
        self.classLabel = -1
        self.gazeData = []
        self.bboxs = []
        self.userGazePoint = (-1, -1)


class MainWindow(QWidget):
    def __init__(self, imageDimension: int):
        super().__init__()
        config = json.load(open('config.json'))
        imageDir = config["image folder"]
        self.imageList = glob.glob(imageDir + '/*.jpg') + glob.glob(imageDir + '/*.png')
        if config["random display order"]:
            random.shuffle(self.imageList)

        # Only one of the mode would work
        self.cheaterMode = config["guide mode"]
        self.instaReviewMode = config["insta review"]
        # the cheater mode, insta review mode, etc, is some kind of extension. self.displayingExtension
        # is a flag of whether the displaying content is a extension.
        self.displayingExtension = False

        self.imageListIndex = 0
        self.data = Data(fileName=self.imageList[0])
        self.imageHeight = config["image height"]
        self.createControlBox()
        self.allowDrawBbox = False
        # This is for the time recording
        self.stopWatch = time.time()
        if imageDimension == 2:
            self.createImageBox2D()
        elif imageDimension == 3:
            self.createImageBox3D()
        else:
            raise Exception('imageDimension must 2 or 3.')
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.imageBox)
        mainLayout.addWidget(self.controlBox)
        self.setLayout(mainLayout)
        self.setWindowTitle("Mic Eye 2.1-beta")
        font = QFont(config['font'], 12)
        font.setBold(True)
        self.setFont(font)

    # This part is about eye track log system
    def setLogSystem(self, volunteerName: str, saveTo: str):
        self.logSystem = CsvLog(volunteerName, saveTo)

    def saveData(self):
        self.logSystem.log(imgName=self.data.fileName,
                           imgClass=self.data.classLabel,
                           gazeData=self.data.gazeData,
                           bboxs=self.data.bboxs,
                           userGazePoint=self.data.userGazePoint)

    # This function controls all the keyboard event
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key_Escape and self.displayingExtension:
            self.nextImage()
            self.displayingExtension = False

        elif (Qt.Key_0 <= key <= Qt.Key_9) and not self.displayingExtension:
            print("time: ",time.time()-self.stopWatch)
            self.data.gazeData = [getPointInImage(x, self.getImageGeometry()) for x in getGazeRaw()]
            self.data.classLabel = chr(key)
            self.saveData()
            if self.instaReviewMode:
                self.instaReview()
                self.displayingExtension = True
            elif self.cheaterMode:
                self.cheaterDisplay()
                self.displayingExtension = True
            else:
                self.nextImage()
        elif key == Qt.Key_L:
            self.drawCrossHair()

    # This part is about bbox drawing
    def __setAllowDrawBboxTrue(self):
        self.allowDrawBbox = True

    def __setAllowDrawBboxFalse(self):
        self.allowDrawBbox = False

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.allowDrawBbox and event.button() == Qt.LeftButton:
            self.__bboxStartX = event.x()
            self.__bboxStartY = event.y()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.allowDrawBbox and event.button() == Qt.LeftButton:
            thisBbox = (self.__bboxStartX, self.__bboxStartY, event.x(), event.y())
            imageX, imageY = (self.imageLabel.frameGeometry().x() + self.imageBox.frameGeometry().x(),
                              self.imageLabel.frameGeometry().y() + self.imageBox.frameGeometry().y())
            thisBbox = (thisBbox[0] - imageX, thisBbox[1] - imageY, thisBbox[2] - imageX, thisBbox[3] - imageY)
            self.data.bboxs.append(thisBbox)
            self.allowDrawBbox = False
            self.drawBBox(*thisBbox)

    def getImageGeometry(self):
        windowGeometry = self.frameGeometry()
        imageGeometry = self.imageLabel.frameGeometry()
        boxGeometry = self.imageBox.frameGeometry()
        imageAbsGeometry = (windowGeometry.x() + imageGeometry.x() + boxGeometry.x(),
                            windowGeometry.y() + imageGeometry.y() + boxGeometry.y(),
                            imageGeometry.width(),
                            imageGeometry.height())
        return imageAbsGeometry

    def drawCrossHair(self):
        image = imRead(self.imageList[self.imageListIndex], targetHeight=self.imageHeight)
        if len(image.shape) == 2:
            # if image is grayscale, make it RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        gaze = getPointInImage(getGazeCenter(lastN=30), self.getImageGeometry())
        crossHair(image, center=(gaze[0], gaze[1]))
        self.imageLabel.setPixmap(createPixmapFromArray(image))

    def nextImage(self):
        self.imageListIndex += 1
        currentImage = imRead(self.imageList[self.imageListIndex], targetHeight=self.imageHeight)
        self.imageLabel.setPixmap(createPixmapFromArray(currentImage))
        # reset the eye tracker and stop watch
        getGazeRaw()
        self.stopWatch=time.time()
        self.data = Data(self.imageList[self.imageListIndex])
        # print(self.imageListIndex)

    def instaReview(self):
        currentImageFile = self.imageList[self.imageListIndex]
        labels = parseLabelmeXMl(currentImageFile)
        currentImage = imRead(self.imageList[self.imageListIndex], targetHeight=self.imageHeight)
        _, originalHeight = getImageFileSize(currentImageFile)
        currentImageWithBBoxes = drawBBoxesOnImage(currentImage, labels, scaleFactor=self.imageHeight / originalHeight)
        gazeHeatmap = pointToHeatmap(self.data.gazeData, heatmapShape=currentImage.shape)
        print(gazeHeatmap.shape,currentImageWithBBoxes.shape)
        imageWithHeatmap = superimposeHeatmapToImage(heatmap=gazeHeatmap, image=currentImageWithBBoxes)
        self.imageLabel.setPixmap(createPixmapFromArray(imageWithHeatmap))

    def cheaterDisplay(self):
        nextImageFile = self.imageList[self.imageListIndex + 1]
        nextImage = imRead(nextImageFile, targetHeight=self.imageHeight)
        _, originalHeight = getImageFileSize(nextImageFile)
        imageWithBBoxes = drawBBoxesOnImage(nextImage, bboxes=parseLabelmeXMl(nextImageFile),
                                            scaleFactor=self.imageHeight / originalHeight)
        self.imageLabel.setPixmap(createPixmapFromArray(imageWithBBoxes))

    def drawBBox(self, x1, y1, x2, y2):
        currentImage = imRead(self.imageList[self.imageListIndex], targetHeight=self.imageHeight)
        cv2.rectangle(img=currentImage,
                      pt1=(x1, y1),
                      pt2=(x2, y2),
                      color=(100, 0, 0),
                      thickness=5)
        self.imageLabel.setPixmap(createPixmapFromArray(currentImage))

    def drawAttentionMap(self):
        pass

    # This function create the UI of Image Display
    def createImageBox2D(self):
        self.imageBox = QGroupBox("")
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(createPixmapFromArray(imRead(self.imageList[0], targetHeight=self.imageHeight)))
        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel)
        self.imageBox.setLayout(layout)

    # This function create the UI of control panel
    def createControlBox(self):
        self.controlBox = QGroupBox("")
        nextButton = QPushButton("Next Image")
        lastButton = QPushButton("Last Image")
        bboxButton = QPushButton("Add Bounding Boxes")
        closeButton = QPushButton("Finish Experiment")

        nextButton.clicked.connect(self.nextImage)
        closeButton.clicked.connect(self.close)
        bboxButton.clicked.connect(self.__setAllowDrawBboxTrue)
        layout = QHBoxLayout()
        layout.addWidget(nextButton)
        layout.addWidget(lastButton)
        layout.addWidget(bboxButton)
        layout.addWidget(closeButton)
        self.controlBox.setLayout(layout)
