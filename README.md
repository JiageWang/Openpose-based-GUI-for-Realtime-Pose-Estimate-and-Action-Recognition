# Openpose-python-cuda10-windows
1. Release of python api of openpose in windows using cuda10 and cudnn7.
2. GUI for easy use
3. Get keypoints from image to local file(TODO)

## Installation
1. install cuda10
2. install cudnn7
3. run `models/getModels.bat` to get model
4. run `pip install opencv-python` to install opencv in python
5. download dll from [https://pan.baidu.com/s/1Cco38Py2G70s559qDt_g6g](https://pan.baidu.com/s/1Cco38Py2G70s559qDt_g6g) password：`64sg` and unzip in your 3rdparty folder
6. run `python openpose_python.py` for run in command line
7. run `python main.py` for run with gui
    * button `Save Result` for saving the current output image and keypoint
    * drop slider to control the output threshold
    * select checkbox to control the keypoint you want to get
    * double click image file in treeview to get openpose result from image


## example
![avatar](media/gui.png)

## References
[Openpose](https://github.com/CMU-Perceptual-Computing-Lab/openpose)
