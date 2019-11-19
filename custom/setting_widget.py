import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

print(os.path.dirname(__file__))


class SettingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main_window = parent
        loadUi("ui/setting_widget.ui", self)

    def save_interval(self):
        return self.doubleSpinBox_interval.value()

    def body_on(self):
        return self.checkBox_body.isChecked()

    def hand_on(self):
        return self.checkBox_hand.isChecked()

    def face_on(self):
        return self.checkBox_face.isChecked()

    def body_threshold(self):
        return self.horizontalSlider_Body.value() / 100

    def hand_threshold(self):
        return self.horizontalSlider_Hand.value() / 100

    def face_threshold(self):
        return self.horizontalSlider_Face.value() / 100

    def net_resolution(self):
        return self.comboBox_resolution.currentText()

    def gesture_on(self):
        return self.checkBox_gesture.isChecked()

    def black_background(self):
        return self.radioButton_black.isChecked()
