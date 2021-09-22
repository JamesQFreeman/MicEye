import cv2
import json
import numpy as np
from utils.imageUtils import imRead, heatmapColormap, superimposeHeatmapToImage

correct = 0
total = 0


def lineProcess(line: str):
    global correct
    global total

    info = line.split(';')
    filename = info[0]
    groundTruth = filename.split('\\')[-2]
    annotation = info[1]
    gaze = json.loads(info[2])
    imgName = filename.split('\\')[-1]
    image = imRead(filename, 800)
    gazeCanvas = np.zeros(image.shape, dtype=np.float)
    for p in gaze:
        x, y = p[0], p[1]
        x = min(799, x)
        y = min(799, y)
        gazeCanvas[y, x] = 1.0
    gazeCanvas = cv2.GaussianBlur(gazeCanvas, (199, 199), 0)
    gazeCanvas = (gazeCanvas - np.min(gazeCanvas))
    gazeCanvas /= np.max(gazeCanvas)

    # res = superimposeHeatmapToImage(heatmap=heatmapColormap(gazeCanvas, cv2.COLORMAP_JET),
    #                                 image=cv2.cvtColor(image, cv2.COLOR_GRAY2RGB))

    res = superimposeHeatmapToImage(heatmap=heatmapColormap(gazeCanvas, cv2.COLORMAP_JET),
                                    image=image)

    res = cv2.putText(res,
                      f'{imgName} \n GT:{groundTruth}|Anno:{annotation}',
                      (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 2,
                      cv2.LINE_AA)
    correct += (groundTruth == annotation)
    total += 1
    print("acc:", correct / total)
    cv2.imshow("", res)
    cv2.waitKey()


for l in open("ZLC2020-10-28-13-36.csv").read().split('\n'):
    lineProcess(l)
