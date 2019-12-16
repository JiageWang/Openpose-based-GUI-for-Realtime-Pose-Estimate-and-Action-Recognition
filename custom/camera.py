import cv2
from PyQt5.QtCore import QTimer


class Camera(object):
    def __init__(self):
        self.device = 0
        self.cap = cv2.VideoCapture()
        self.timer = QTimer()

    def stop(self):
        self.timer.stop()
        self.cap.release()
        return True

    def pause(self):
        self.timer.stop()

    def begin(self):
        self.timer.start(20)

    def start(self, device):
        if self.cap.isOpened():
            self.cap.release()
        self.timer.start(20)
        self.cap.open(device)
        self.device = device
        return True

    def restart(self):
        self.start(self.device)

    @property
    def is_pause(self):
        return self.cap.isOpened() and not self.timer.isActive()

    @property
    def is_open(self):
        return self.cap.isOpened()

    @property
    def frame(self):
        if self.is_open and not self.is_pause:
            return self.cap.read()[1]

    @property
    def frame_count(self):
        if self.is_open:
            return self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    @property
    def frame_pos(self):
        if self.is_open:
            return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    @frame_pos.setter
    def frame_pos(self, value):
        if self.is_open:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)

    @property
    def resolution(self):
        if self.is_open:
            return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
