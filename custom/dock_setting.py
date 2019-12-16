import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.uic import loadUi

print(os.path.dirname(__file__))


class SettingDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        loadUi("ui/dock_setting.ui", self)
        self.dock_label = QLabel("Openpose Settings")
        self.dock_label.setMinimumHeight(30)
        self.dock_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setTitleBarWidget(self.dock_label)

        # 信号与槽
        self.horizontalSlider_Body.sliderReleased.connect(self.change_body_threshold)
        self.horizontalSlider_Face.sliderReleased.connect(self.change_face_threshold)
        self.horizontalSlider_Hand.sliderReleased.connect(self.change_hand_threshold)
        self.checkBox_body.stateChanged.connect(self.check_body)  # 状态改变触发check_box_changed函数
        self.checkBox_hand.stateChanged.connect(self.check_hand)  # 状态改变触发check_box_changed函数
        self.checkBox_face.stateChanged.connect(self.check_face)  # 状态改变触发check_box_changed函数
        self.radioButton_black.toggled.connect(self.change_background)
        self.comboBox_resolution.currentIndexChanged.connect(self.change_resolution)

        self.hide()

    def check_body(self, status):
        # 姿态估计
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.horizontalSlider_Body.setEnabled(flag)
        self.radioButton_black.setEnabled(flag)
        self.radioButton_rgb.setEnabled(flag)
        self.parent().openpose_model.update_wrapper("render_pose", render_pose)

    def check_hand(self, status):
        # 手部估计
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Hand.setEnabled(flag)
        self.checkBox_gesture.setEnabled(flag)
        self.parent().openpose_model.update_wrapper("hand", flag)

    def check_face(self, status):
        # 脸部估计
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Face.setEnabled(flag)
        self.checkBox_emotion.setEnabled(flag)
        self.parent().openpose_model.update_wrapper("face", flag)

    def change_body_threshold(self):
        # 姿态估计阈值
        value = self.body_threshold
        self.label_threshold_body.setText(str(value * 100))
        self.parent().openpose_model.update_wrapper("render_threshold", value)

    def change_hand_threshold(self):
        # 手部估计阈值
        value = self.hand_threshold
        self.label_threshold_hand.setText(str(value * 100))
        self.parent().update_wrapper("hand_render_threshold", value)

    def change_face_threshold(self):
        # 脸部估计阈值
        value = self.face_threshold
        self.label_threshold_face.setText(str(value * 100))
        self.parent().openpose_model.update_wrapper("face_render_threshold", value)

    def change_resolution(self):
        resolution = self.net_resolution
        self.parent().openpose_model.update_wrapper("net_resolution", resolution)

    def change_background(self):
        black_background = self.black_background
        self.parent().openpose_model.update_wrapper("disable_blending", black_background)

    @property
    def save_interval(self):
        return self.doubleSpinBox_interval.value()

    @property
    def body_on(self):
        return self.checkBox_body.isChecked()

    @property
    def hand_on(self):
        return self.checkBox_hand.isChecked()

    @property
    def face_on(self):
        return self.checkBox_face.isChecked()

    @property
    def body_threshold(self):
        return self.horizontalSlider_Body.value() / 100

    @property
    def hand_threshold(self):
        return self.horizontalSlider_Hand.value() / 100

    @property
    def face_threshold(self):
        return self.horizontalSlider_Face.value() / 100

    @property
    def net_resolution(self):
        return self.comboBox_resolution.currentText()

    @property
    def gesture_on(self):
        return self.checkBox_gesture.isChecked()

    @property
    def black_background(self):
        return self.radioButton_black.isChecked()

