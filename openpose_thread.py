import os
import cv2
import sys

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt5.QtGui import QImage, QPixmap

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    sys.path.append(dir_path + '/openpose')
    os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/openpose;' + dir_path + '/3rdparty;'
    import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. \
            Did you enable `BUILD_PYTHON` in CMake and \
            have this Python script in the right folder?')
    raise e


class OpenposeThead(QThread):
    signal = pyqtSignal(op.Datum)
    """多线程处理图像"""

    def __init__(self, label, op_wrapper, datum):
        super(OpenposeThead, self).__init__()
        self.cap = cv2.VideoCapture()
        self.label = label
        self.op_wrapper = op_wrapper
        self.datum = datum
        self.mutex = QMutex()

    def run(self):
        self.cap.open(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.op_wrapper.start()
        while True:
            ret, frame = self.cap.read()
            with QMutexLocker(self.mutex):
                self.datum.cvInputData = frame
                self.op_wrapper.emplaceAndPop([self.datum])
                self.updata_label(self.datum.cvOutputData)

    def updata_label(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        h, w, c = img.shape  # 获取图片形状
        image = QImage(img, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)

    def terminate(self):
        if self.cap.isOpened():
            self.cap.release()
        self.label.clear()
        super().terminate()
