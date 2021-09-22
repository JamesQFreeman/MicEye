import TobiiEyeTracker


def getGazeCenter(lastN: int = 100) -> tuple:
    buffers = TobiiEyeTracker.getBuffer()
    if len(buffers) == 0:
        return None
    availableSize = min(lastN, len(buffers))
    x = 0.0
    y = 0.0
    for point in buffers[-availableSize:]:
        x += point[0]
        y += point[1]
    return int(x / availableSize * 1920), int(y / availableSize * 1080)


def getGazeRaw():
    return [[int(p[0] * 1920), int(p[1] * 1080)] for p in TobiiEyeTracker.getBuffer()]


def refresh():
    TobiiEyeTracker.getBuffer()


def eyeTrackerInit():
    try:
        TobiiEyeTracker.init()
    except:
        pass
