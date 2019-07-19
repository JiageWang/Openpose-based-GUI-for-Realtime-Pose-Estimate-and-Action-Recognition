import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox, QSlider, QDirModel

from ui.main_window import Ui_MainWindow  # 由qtdesigner 生成的布局
from openpose_thread import OpenposeThead


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Openpose GUI")
        self.setWindowIcon(QIcon('media/logo.png'))

        self.param = {
            "model_folder": "models/",
            "body": 1,
            "render_pose": 0,
            "render_threshold": 0.1,
            "hand": False,
            "hand_render": 1,
            "hand_render_threshold": 0.2,
            "face": False,
            "face_render": 1,
            "face_render_threshold": 0.4,
            "disable_blending": False  # black blackgroud if True
        }

        self.openpose_thread = OpenposeThead(self.label_frame, self.param)

        # 初始化复选框
        self.checkBox_body.stateChanged.connect(self.checkBody)  # 状态改变触发check_box_changed函数
        self.checkBox_hand.stateChanged.connect(self.checkHand)  # 状态改变触发check_box_changed函数
        self.checkBox_face.stateChanged.connect(self.checkFace)  # 状态改变触发check_box_changed函数
        self.checkBox_body.setChecked(False)  # 默认设置为选中
        self.checkBox_hand.setChecked(False)  # 默认设置为选中
        self.checkBox_face.setChecked(False)  # 默认设置为选中

        # 初始化滑动条
        self.horizontalSlider_Body.setEnabled(False)
        self.horizontalSlider_Hand.setEnabled(False)
        self.horizontalSlider_Face.setEnabled(False)
        self.horizontalSlider_Body.setMaximum(100)
        self.horizontalSlider_Body.setMinimum(0)
        self.horizontalSlider_Body.setValue(5)
        self.horizontalSlider_Body.valueChanged.connect(self.changeBodyThreshold)
        self.horizontalSlider_Hand.setMaximum(100)
        self.horizontalSlider_Hand.setMinimum(0)
        self.horizontalSlider_Hand.setValue(20)
        self.horizontalSlider_Hand.valueChanged.connect(self.changeHandThreshold)
        self.horizontalSlider_Face.setMaximum(100)
        self.horizontalSlider_Face.setMinimum(0)
        self.horizontalSlider_Face.setValue(20)
        self.horizontalSlider_Face.valueChanged.connect(self.changeFaceThreshold)

        tree_model = QDirModel()
        self.treeView_file.setModel(tree_model)
        self.treeView_file.setRootIndex(tree_model.index(os.getcwd()))
        self.treeView_file.show()

        self.label_frame.setScaledContents(True)
        self.openpose_thread.start()

    def checkBody(self, status):
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.horizontalSlider_Body.setEnabled(flag)
        self.param["render_pose"] = render_pose
        self.openpose_thread.config_wrapper(self.param)

    def checkHand(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Hand.setEnabled(flag)
        self.param["hand"] = flag
        self.openpose_thread.config_wrapper(self.param)

    def checkFace(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Face.setEnabled(flag)
        self.param["face"] = flag
        self.openpose_thread.config_wrapper(self.param)

    def changeBodyThreshold(self):
        self.body_threshold = self.horizontalSlider_Body.value()

    def changeHandThreshold(self):
        self.hand_threshold = self.horizontalSlider_Hand.value()

    def changeFaceThreshold(self):
        self.face_threshold = self.horizontalSlider_Face.value()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
