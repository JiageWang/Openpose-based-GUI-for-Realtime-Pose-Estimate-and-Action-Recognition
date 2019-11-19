from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.uic import loadUi


class MediaControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        loadUi("ui/media_control.ui", self)

        self.play_button.setCheckable(True)
        self.process_slider.setMinimum(0)

    def update(self, pos, frames):
        self.process_slider.setMaximum(frames)
        self.process_slider.setValue(pos)

    def slider_pos(self):
        return self.process_slider.value()

    def is_play(self):
        return self.play_button.isChecked()

    @property
    def frame_pos(self):
        return self.process_slider.value()

    def play(self):
        self.play_button.setIcon(QIcon("icon/pause.png"))
        self.play_button.setChecked(True)

    def pause(self):
        self.play_button.setIcon(QIcon("icon/play.png"))
        self.play_button.setChecked(False)

