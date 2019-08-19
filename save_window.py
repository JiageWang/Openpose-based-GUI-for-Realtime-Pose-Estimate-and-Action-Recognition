import os
import time
import numpy as np
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class SaveWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("ui/save_window.ui", self)
        self.setWindowIcon(QIcon('media/snipaste.png'))
        self.setWindowTitle("Snipaste")
        self.body_keypoint = None
        self.hand_keypoint = None
        self.face_keypoint = None
        self.pushButton_save.clicked.connect(self.saveCurrent)
        self.pushButton_cancel.clicked.connect(self.cancelSnipaste)
        self.output_path = "output"
        self.output_img_path = os.path.join(self.output_path, "img")
        self.output_body_path = os.path.join(self.output_path, "body")
        self.output_hand_path = os.path.join(self.output_path, "hand")
        self.output_face_path = os.path.join(self.output_path, "face")
        self.init_out_path()
        self.count = 0

    def init_out_path(self):
        if not os.path.exists(self.output_img_path):
            os.makedirs(self.output_img_path)
        if not os.path.exists(self.output_hand_path):
            os.makedirs(self.output_hand_path)
        if not os.path.exists(self.output_body_path):
            os.makedirs(self.output_body_path)
        if not os.path.exists(self.output_face_path):
            os.makedirs(self.output_face_path)

    def saveCurrent(self):
        self.count += 1
        self.label_frame.pixmap().save(os.path.join(self.output_img_path, "{:0>4d}.jpg".format(self.count)))
        if self.body_keypoint is not None:
            np.save(os.path.join(self.output_body_path, "{:0>4d}_body.npy".format(self.count)), self.body_keypoint)
            self.body_keypoint = None
        if self.hand_keypoint is not None:
            np.save(os.path.join(self.output_hand_path, "{:0>4d}_hand.npy".format(self.count)), self.hand_keypoint)
            self.hand_keypoint = None
        if self.face_keypoint is not None:
            np.save(os.path.join(self.output_face_path, "{:0>4d}_face.npy".format(self.count)), self.face_keypoint)
            self.face_keypoint = None
        self.close()

    def cancelSnipaste(self):
        self.setHidden(True)
        self.close()

    def setFrame(self, pixmap, body_keyppoint, hand_keypoint, face_keypoint):
        self.label_frame.setPixmap(pixmap)
        self.body_keypoint = body_keyppoint
        self.hand_keypoint = hand_keypoint
        self.face_keypoint = face_keypoint
        self.show()
