import time
import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class SaveWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("ui/save_window.ui", self)
        # self.setupUi(self)
        self.setWindowTitle("Snipaste")
        self.body_keypoint = None
        self.hand_keypoint = None
        self.pushButton_save.clicked.connect(self.saveCurrent)
        self.pushButton_cancel.clicked.connect(self.cancelSnipaste)

    def saveCurrent(self):
        timestamp = str(int(time.time()))
        print("saving ", timestamp)
        self.label_frame.pixmap().save("{}.jpg".format(timestamp))
        if self.body_keypoint is not None:
            np.save("{}_body.npy".format(timestamp), self.body_keypoint)
            self.body_keypoint = None
        if self.hand_keypoint is not None:
            np.save("{}_hand.npy".format(timestamp), self.hand_keypoint)
            self.hand_keypoint = None
        self.close()

    def cancelSnipaste(self):
        self.setHidden(True)
        self.close()

    def setFrame(self, pixmap, body_keyppoint, hand_keypoint):
        self.label_frame.setPixmap(pixmap)
        self.body_keypoint = body_keyppoint
        self.hand_keypoint = hand_keypoint
        self.show()
