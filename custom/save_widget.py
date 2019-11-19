import os
import numpy as np
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class SaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main_window = parent
        loadUi("ui/save_widget.ui", self)
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
        self.hide()

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
        self.save(self.label_frame.pixmap(), self.body_keypoint, self.hand_keypoint, self.face_keypoint)

    def cancelSnipaste(self):
        self.setHidden(True)
        self.close()

    def setFrame(self, pixmap, body_keypoint, hand_keypoint, face_keypoint, message=None):
        self.setWindowTitle(message)
        self.label_frame.setPixmap(pixmap)
        self.body_keypoint = body_keypoint
        self.hand_keypoint = hand_keypoint
        self.face_keypoint = face_keypoint
        self.show()

    def save(self, pixmap, body_keypoints, hand_keypoints, face_keypoints):
        pixmap.save(os.path.join(self.output_img_path, "{:0>4d}.jpg".format(self.count)))
        if body_keypoints is not None:
            np.save(os.path.join(self.output_body_path, "{:0>4d}_body.npy".format(self.count)), body_keypoints)
        if hand_keypoints is not None:
            np.save(os.path.join(self.output_hand_path, "{:0>4d}_hand.npy".format(self.count)), hand_keypoints)
        if face_keypoints is not None:
            np.save(os.path.join(self.output_face_path, "{:0>4d}_face.npy".format(self.count)), face_keypoints)
        self.count += 1
