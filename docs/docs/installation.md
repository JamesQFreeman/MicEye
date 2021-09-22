# Installation
Plug in your eye-tracker, and set it up.
## Long story short
If you are an experienced programmer and know what you are doing, just install a win-32 python and git clone. Or you can find more detail below.
```bash
set CONDA_SUBDIR=win-32 
conda create -n miceye python=3.7
conda activate miceye
git clone https://github.com/JamesQFreeman/MICEYE.git
pip install python-opencv PyQt5 numpy pillow
cd MICEYE
python MicEye.py
```
## System
Since Tobii's sdk did not compile on Linux or MacOS, we use **Windows 10**. You can read [tobii's doc](https://developer.tobii.com/product-integration/stream-engine/) for more details. In this project, we just use the PyEyetracker I wrote. If you want more than gaze location, see [PyEyetracker](https://github.com/JamesQFreeman/PyEyetracker) and write your own. 

## Python Environment
It is because the ```tobii_stream_engine.dll``` is compiled in 32-bit instead of AMD64, we have to use 32-bit python. If you got conda, it shouldn't be too hard:
```bash
set CONDA_SUBDIR=win-32 
conda create -n miceye python=3.7
```
If you haven't got conda, just download an [anaconda](https://docs.anaconda.com/anaconda/install/windows/) or a miniconda.

## Dependency
All the image processing is opencv/numpy style and all the GUI is wrote in PyQt5, so you need to install these as well
```bash
pip install python-opencv PyQt5 numpy pillow
```

## Download MicEye
You can git clone or download the zip from Github
```bash
git clone https://github.com/JamesQFreeman/MICEYE.git
```
Then you are good to go!