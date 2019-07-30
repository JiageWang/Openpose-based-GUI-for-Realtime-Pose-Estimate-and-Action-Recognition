import os
import sys
import cv2
import copy

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QDirModel, QFileDialog, QMessageBox, QPushButton
from PyQt5.uic import loadUi

from save_window import SaveWindow

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


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        loadUi("ui/main_window.ui", self)
        self.setWindowTitle("Openpose GUI")
        self.setWindowIcon(QIcon('media/logo.png'))

        self.params = {
            # "net_resolution": "128x96",
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

        self.datum = op.Datum()
        self.op_wrapper = op.WrapperPython()
        self.tree_model = QDirModel()
        self.cap = cv2.VideoCapture()
        self.timer = QTimer()
        self.timer.timeout.connect(self.showFrame)
        self.save_window = SaveWindow()
        self.webcam_open = False

        self.initOpenpose()
        self.initCheckBox()
        self.initPushButton()
        self.initRadioButton()
        self.initSlider()
        self.initTreeview()
        self.initOthers()

    def initOpenpose(self):
        self.op_wrapper.configure(self.params)
        self.op_wrapper.start()

    def initCheckBox(self):
        self.checkBox_body.setChecked(False)  # 默认设置为选中
        self.checkBox_hand.setChecked(False)  # 默认设置为选中
        self.checkBox_face.setChecked(False)  # 默认设置为选中
        self.checkBox_body.stateChanged.connect(self.checkBody)  # 状态改变触发check_box_changed函数
        self.checkBox_hand.stateChanged.connect(self.checkHand)  # 状态改变触发check_box_changed函数
        self.checkBox_face.stateChanged.connect(self.checkFace)  # 状态改变触发check_box_changed函数


    def initRadioButton(self):
        self.radioButton_black.setEnabled(False)
        self.radioButton_rgb.setEnabled(False)
        self.radioButton_black.setChecked(False)
        self.radioButton_rgb.setChecked(True)
        self.radioButton_black.toggled.connect(self.changeBackground)
        # self.radioButton_rgb.toggled.connect(self.changeBackground)

    def initPushButton(self):
        self.pushButton_webcam.clicked.connect(self.runWebcam)
        self.pushButton_folder.clicked.connect(self.changeFolder)
        self.pushButton_save.clicked.connect(self.saveCurrent)
        self.pushButton_record.clicked.connect(self.beginRecord)

    def initSlider(self):
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
        self.horizontalSlider_Body.sliderReleased.connect(self.changeBodyThreshold)
        self.horizontalSlider_Face.sliderReleased.connect(self.changeFaceThreshold)
        self.horizontalSlider_Hand.sliderReleased.connect(self.changeHandThreshold)

    def initTreeview(self):
        # 目录树
        self.treeView_file.setModel(self.tree_model)
        self.treeView_file.setRootIndex(self.tree_model.index(os.getcwd()))
        self.treeView_file.show()
        self.treeView_file.doubleClicked.connect(self.treeClicked)

    def initOthers(self):
        # 图像显示标签
        self.label_frame.setScaledContents(True)

    def showFrame(self):
        _, frame = self.cap.read()
        img = self.openposeImage(frame)
        self.updateLabel(img)

    def treeClicked(self, file_index):
        file_name = self.tree_model.filePath(file_index)
        if file_name.endswith(('.jpg', '.png')):
            if self.webcam_open:
                QMessageBox.information(self, "Note", "Please stop webcam first", QMessageBox.Yes)
                return
            img = cv2.imread(file_name)
            result = self.openposeImage(img)
            self.updateLabel(result)

    def updateLabel(self, frame):
        h, w, c = frame.shape  # 获取图片形状
        image = QImage(frame, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label_frame.setPixmap(pixmap)

    def openposeImage(self, img):
        self.datum.cvInputData = img
        self.op_wrapper.emplaceAndPop([self.datum])
        result = self.datum.cvOutputData
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        return result

    def changeBackground(self):
        if self.radioButton_black.isChecked():
            self.params['disable_blending'] = True
        else:
            self.params['disable_blending'] = False
        self.updateWrapper()

    def changeFolder(self):
        folder_name = QFileDialog.getExistingDirectory(self, '标题', './')  # 可设置默认路径
        if folder_name:
            self.treeView_file.setRootIndex(self.tree_model.index(folder_name))
            self.treeView_file.show()

    def saveCurrent(self):
        pixmap = self.label_frame.pixmap()
        if pixmap:
            body_keypoint = copy.deepcopy(self.datum.poseKeypoints) if self.checkBox_body.isChecked() else None
            hand_keypoint = copy.deepcopy(self.datum.handKeypoints) if self.checkBox_hand.isChecked() else None
            face_keypoint = copy.deepcopy(self.datum.faceKeypoints) if self.checkBox_face.isChecked() else None
            self.save_window.setFrame(pixmap.copy(), body_keypoint, hand_keypoint, face_keypoint)
            self.save_window.show()
        else:
            QMessageBox.warning(self, "Note", "No data in frame", QMessageBox.Yes)

    def beginRecord(self):
        pass

    def runWebcam(self):
        if self.webcam_open:
            self.webcam_open = False
            self.cap.release()
            self.label_frame.clear()
            self.timer.stop()
            self.pushButton_webcam.setText("Open Webcam")
        else:
            self.webcam_open = True
            self.cap.open(0)
            self.timer.start(20)
            self.pushButton_webcam.setText("Stop Webcam")

    def checkBody(self, status):
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.horizontalSlider_Body.setEnabled(flag)
        self.radioButton_black.setEnabled(flag)
        self.radioButton_rgb.setEnabled(flag)
        self.params["render_pose"] = render_pose
        self.updateWrapper()

    def checkHand(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Hand.setEnabled(flag)
        self.params["hand"] = flag
        self.updateWrapper()

    def checkFace(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Face.setEnabled(flag)
        self.params["face"] = flag
        self.updateWrapper()

    def changeBodyThreshold(self):
        value = self.horizontalSlider_Body.value()
        print(value)
        self.params["render_threshold"] = value / 100
        self.label_threshold_body.setText(str(value))
        self.updateWrapper()

    def changeHandThreshold(self):
        value = self.horizontalSlider_Hand.value()
        print(value)
        self.params["hand_render_threshold"] = value / 100
        self.label_threshold_hand.setText(str(value))
        self.updateWrapper()

    def changeFaceThreshold(self):
        value = self.horizontalSlider_Face.value()
        print(value)
        self.params["face_render_threshold"] = value / 100
        self.label_threshold_face.setText(str(value))
        self.updateWrapper()

    def updateWrapper(self):
        self.op_wrapper.configure(self.params)
        self.op_wrapper.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
