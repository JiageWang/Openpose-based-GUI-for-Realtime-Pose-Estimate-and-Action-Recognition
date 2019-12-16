import os
import json
import numpy as np
from PyQt5.QtGui import QIcon, QPixmap

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

        self.pushButton_save.clicked.connect(self.save_current)
        self.pushButton_cancel.clicked.connect(self.cancel_snipaste)

        self.init_out_path()
        self.count = 0
        self.hide()

    def init_out_path(self):
        self.output_path = "output"
        self.output_img_path = os.path.join(self.output_path, "img")
        self.output_body_path = os.path.join(self.output_path, "body")
        self.output_hand_path = os.path.join(self.output_path, "hand")
        self.output_face_path = os.path.join(self.output_path, "face")
        if not os.path.exists(self.output_img_path):
            os.makedirs(self.output_img_path)
        if not os.path.exists(self.output_hand_path):
            os.makedirs(self.output_hand_path)
        if not os.path.exists(self.output_body_path):
            os.makedirs(self.output_body_path)
        if not os.path.exists(self.output_face_path):
            os.makedirs(self.output_face_path)

    def save_current(self):
        self.save(self.label_frame.pixmap(), self.body_keypoint, self.hand_keypoint, self.face_keypoint)
        self.hide()

    def cancel_snipaste(self):
        self.setHidden(True)
        self.close()

    def set_frame(self, pixmap, body_keypoint, hand_keypoint, face_keypoint, message=None):
        self.setWindowTitle(message)
        self.label_frame.setPixmap(pixmap)
        self.body_keypoint = body_keypoint
        self.hand_keypoint = hand_keypoint
        self.face_keypoint = face_keypoint
        self.show()

    def save(self, pixmap, body_keypoints, hand_keypoints, face_keypoints):
        pixmap.save(os.path.join(self.output_img_path, "{:0>4d}.jpg".format(self.count)))
        w = pixmap.width()
        h = pixmap.height()
        if body_keypoints is not None:
            np.save(os.path.join(self.output_body_path, "{:0>4d}_body.json".format(self.count)), body_keypoints)
            self.body_npy2json(body_keypoints, w, h)
        if hand_keypoints is not None:
            np.save(os.path.join(self.output_hand_path, "{:0>4d}_hand.json".format(self.count)), hand_keypoints)
            self.hand_npy2json(hand_keypoints, w, h)
        if face_keypoints is not None:
            np.save(os.path.join(self.output_face_path, "{:0>4d}_face.json".format(self.count)), face_keypoints)
            self.face_npy2json(face_keypoints, w, h)
        self.count += 1

    def hand_npy2json(self, npy, w, h):
        file = os.path.join(self.output_hand_path, "{:0>4d}_hand.json".format(self.count))
        dic = {}
        person_number = npy[0].shape[0]
        dic["person_number"] = person_number
        dic["width"] = w
        dic["height"] = h
        dic["hand_keypoints"] = []
        for i in range(person_number):
            dic["hand_keypoints"].append({"left_hand_keypoints": npy[0][i].tolist()})
            dic["hand_keypoints"].append({"right_hand_keypoints": npy[1][i].tolist()})
        with open(file, 'w') as f:
            json.dump(dic, f)

    def body_npy2json(self, npy, w, h):
        file = os.path.join(self.output_body_path, "{:0>4d}_body.json".format(self.count))
        dic = {}
        person_number = npy.shape[0]
        dic["person_number"] = person_number
        dic["width"] = w
        dic["height"] = h
        dic["body_keypoints"] = []
        for i in range(person_number):
            dic["body_keypoints"].append(npy[i].tolist())
        with open(file, 'w') as f:
            json.dump(dic, f)

    def face_npy2json(self, npy, w, h):
        file = os.path.join(self.output_face_path, "{:0>4d}_face.json".format(self.count))
        dic = {}
        person_number = npy.shape[0]
        dic["person_number"] = person_number
        dic["width"] = w
        dic["height"] = h
        dic["face_keypoints"] = []
        for i in range(person_number):
            dic["face_keypoints"].append(npy[i].tolist())
        with open(file, 'w') as f:
            json.dump(dic, f)
