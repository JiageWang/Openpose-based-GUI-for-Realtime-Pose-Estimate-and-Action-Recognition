import cv2
from PyQt5.QtCore import QTimer


class Camera(object):
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_pause = False
        self.cap = cv2.VideoCapture()
        self.timer = QTimer()

    def stop(self):
        if not self.cap.isOpened():
            return False
        self.timer.stop()
        self.cap.release()
        return True

    def start(self, device=0):
        if self.cap.isOpened():
            return False
        self.timer.start(20)
        self.cap.open(device)
        return True

    def frame(self):
        if self.cap.isOpened() and not self.is_pause:
            return self.cap.read()[1]

    def is_open(self):
        return self.cap.isOpened()

    @property
    def frame_count(self):
        if self.cap.isOpened():
            return self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    @property
    def frame_pos(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    @frame_pos.setter
    def frame_pos(self, value):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)

    @property
    def resolution(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
