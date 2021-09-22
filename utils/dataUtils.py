from datetime import datetime
import os
from typing import List, Tuple


# This C in csv stand for semicolon
# TODO: This is a rubbish code, I will replace it by json, but I would like to do it another day.
class CsvLog:
    def __init__(self, volunteerName: str, saveTo: str):
        datetimeObj = datetime.now()
        experienceTime = f"{datetimeObj.year}-{datetimeObj.month}-{datetimeObj.day}-{datetimeObj.hour}-{datetimeObj.minute}"
        if not os.path.exists(saveTo):
            os.makedirs(saveTo)
        self.filename = saveTo + '/' + volunteerName + experienceTime + '.csv'
        self.fp = open(self.filename, 'a')

    def log(self,
            imgName: str,
            imgClass: int,
            gazeData: List[Tuple[int, int]],
            bboxs: List[Tuple[int, int, int, int]],
            userGazePoint: Tuple[int, int]):
        self.fp.write(f"{imgName};{imgClass};{gazeData};{bboxs};{userGazePoint}\n")
