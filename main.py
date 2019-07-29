import os
import sys
import cgitb

import cv2

cgitb.enable(format='text')

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QDirModel, QFileDialog, QWidget, QLabel
# from PyQt5.uic import loadUiType

from ui.main_window import Ui_MainWindow  # 由qtdesigner 生成的布局
from openpose_thread import OpenposeThead

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    sys.path.append(dir_path + '/openpose')
    os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/openpose;' + dir_path + '/3rdparty;'
    import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. \
            Did you enable `BUILD_PYTHON` in CMake and \
            have this Python script in the right folder?')
    raise e

from ui.snipaste_window import Ui_Snipaste


class SnipasteWindow(QWidget, Ui_Snipaste):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Snipaste")
        self.pushButton_save.clicked.connect(self.saveSnipaste)
        self.pushButton_cancel.clicked.connect(self.cancelSnipaste)

    def saveSnipaste(self):
        self.label_frame.pixmap().save("1.jpg")
        self.setHidden(True)

    def cancelSnipaste(self):
        self.setHidden(True)

    def setPixmap(self, pixmap):
        self.label_frame.setPixmap(pixmap)


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Openpose GUI")
        self.setWindowIcon(QIcon('media/logo.png'))

        # Init openpose
        self.params = {
            "net_resolution": "128x96",
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

        self.op_wrapper = op.WrapperPython()
        self.op_wrapper.configure(self.params)
        self.openpose_thread = OpenposeThead(self.label_frame, self.op_wrapper)

        # 初始化复选框
        self.checkBox_body.setChecked(False)  # 默认设置为选中
        self.checkBox_hand.setChecked(False)  # 默认设置为选中
        self.checkBox_face.setChecked(False)  # 默认设置为选中
        self.checkBox_body.stateChanged.connect(self.checkBody)  # 状态改变触发check_box_changed函数
        self.checkBox_hand.stateChanged.connect(self.checkHand)  # 状态改变触发check_box_changed函数
        self.checkBox_face.stateChanged.connect(self.checkFace)  # 状态改变触发check_box_changed函数

        # 单选框
        self.radioButton_black.setChecked(False)
        self.radioButton_rgb.setChecked(True)
        self.radioButton_black.toggled.connect(self.changeBackground)
        self.radioButton_rgb.toggled.connect(self.changeBackground)


        # config pushButton
        self.pushButton_webcam.clicked.connect(self.runWebcam)
        self.pushButton_folder.clicked.connect(self.changeFolder)
        self.pushButton_snipaste.clicked.connect(self.getSnipaste)

        # 初始化滑动条
        self.horizontalSlider_Body.setEnabled(False)
        self.horizontalSlider_Hand.setEnabled(False)
        self.horizontalSlider_Face.setEnabled(False)
        self.horizontalSlider_Body.setMaximum(100)
        self.horizontalSlider_Body.setMinimum(0)
        self.horizontalSlider_Body.setValue(1)
        self.horizontalSlider_Hand.setMaximum(100)
        self.horizontalSlider_Hand.setMinimum(0)
        self.horizontalSlider_Hand.setValue(20)
        self.horizontalSlider_Face.setMaximum(100)
        self.horizontalSlider_Face.setMinimum(0)
        self.horizontalSlider_Face.setValue(40)
        self.label_threshold_body.setText(str(1))
        self.label_threshold_hand.setText(str(20))
        self.label_threshold_face.setText(str(40))
        self.horizontalSlider_Body.valueChanged.connect(self.changeBodyThreshold)
        self.horizontalSlider_Face.valueChanged.connect(self.changeFaceThreshold)
        self.horizontalSlider_Hand.valueChanged.connect(self.changeHandThreshold)

        # 目录树
        self.tree_model = QDirModel()
        self.treeView_file.setModel(self.tree_model)
        self.treeView_file.setRootIndex(self.tree_model.index(os.getcwd()))
        self.treeView_file.show()
        self.treeView_file.doubleClicked.connect(self.treeClicked)

        # 图像显示标签
        self.label_frame.setScaledContents(True)
        self.snipaste = SnipasteWindow()

    def treeClicked(self, file_index):
        file_name = self.tree_model.filePath(file_index)
        if file_name.endswith(('.jpg', '.png')):
            img = cv2.imread(file_name)
            result = self.openpose_image(img)
            h, w, c = result.shape  # 获取图片形状
            result = QImage(result, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(result)
            self.label_frame.setPixmap(pixmap)

    def openpose_image(self, img):
        datum = op.Datum()
        datum.cvInputData = img
        self.op_wrapper.emplaceAndPop([datum])
        result = datum.cvOutputData
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        return result

    def changeBackground(self):
        if self.radioButton_black.isChecked():
            self.params['disable_blending'] = True
        else:
            self.params['disable_blending'] = False
        self.update_wrapper()


    def changeFolder(self):
        folder_name = QFileDialog.getExistingDirectory(self, '标题', './')  # 可设置默认路径
        if folder_name:
            self.treeView_file.setRootIndex(self.tree_model.index(folder_name))
            self.treeView_file.show()

    def getSnipaste(self):
        pixmap = self.label_frame.pixmap()
        if pixmap:
            self.snipaste.setPixmap(pixmap)
            self.snipaste.show()

    def runWebcam(self):
        if self.pushButton_webcam.text() == "Open Webcam":
            self.openpose_thread.start()
            self.pushButton_webcam.setText("Stop Webcam")
        else:
            self.openpose_thread.terminate()
            self.pushButton_webcam.setText("Open Webcam")

    def checkBody(self, status):
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.horizontalSlider_Body.setEnabled(flag)
        self.params["render_pose"] = render_pose
        self.update_wrapper()

    def checkHand(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Hand.setEnabled(flag)
        self.params["hand"] = flag
        self.update_wrapper()

    def checkFace(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Face.setEnabled(flag)
        self.params["face"] = flag
        self.update_wrapper()

    def changeBodyThreshold(self):
        value = self.horizontalSlider_Body.value()
        print(value)
        self.params["render_threshold"] = value/100
        self.label_threshold_body.setText(str(value))
        self.update_wrapper()

    def changeHandThreshold(self):
        value = self.horizontalSlider_Hand.value()
        print(value)
        self.params["hand_render_threshold"] = value/100
        self.label_threshold_hand.setText(str(value))
        self.update_wrapper()

    def changeFaceThreshold(self):
        value = self.horizontalSlider_Face.value()
        print(value)
        self.params["face_render_threshold"] = value/100
        self.label_threshold_face.setText(str(value))
        self.update_wrapper()

    def update_wrapper(self):
        self.op_wrapper.configure(self.params)
        print('restart')
        self.op_wrapper.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
