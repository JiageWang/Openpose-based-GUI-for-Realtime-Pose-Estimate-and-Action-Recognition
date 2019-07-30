import os
import sys
import cv2
import copy
import time

import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QDirModel, QFileDialog, QMessageBox
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
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.cap = cv2.VideoCapture()

        self.save_window = SaveWindow()

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_frame)

        self.out_path = "output"
        self.out_img_path = os.path.join(self.out_path, "{}/img")
        self.out_body_path = os.path.join(self.out_path, "{}/keypoint_body")
        self.out_hand_path = os.path.join(self.out_path, "{}/keypoint_hand")
        self.out_face_path = os.path.join(self.out_path, "{}/keypoint_face")

        self.webcam_open = False
        self.is_writing = False
        self.timestamp = ""
        self.start_time = 0
        self.count = 0

        self.init_openpose()
        self.init_checkbox()
        self.init_pushbutton()
        self.init_radiobutton()
        self.init_slider()
        self.init_treeview()
        self.init_others()

    def init_openpose(self):
        self.op_wrapper.configure(self.params)
        self.op_wrapper.start()

    def init_checkbox(self):
        self.checkBox_body.setChecked(False)  # 默认设置为选中
        self.checkBox_hand.setChecked(False)  # 默认设置为选中
        self.checkBox_face.setChecked(False)  # 默认设置为选中
        self.checkBox_body.stateChanged.connect(self.check_body)  # 状态改变触发check_box_changed函数
        self.checkBox_hand.stateChanged.connect(self.check_hand)  # 状态改变触发check_box_changed函数
        self.checkBox_face.stateChanged.connect(self.check_face)  # 状态改变触发check_box_changed函数

    def init_radiobutton(self):
        self.radioButton_black.setEnabled(False)
        self.radioButton_rgb.setEnabled(False)
        self.radioButton_black.setChecked(False)
        self.radioButton_rgb.setChecked(True)
        self.radioButton_black.toggled.connect(self.change_background)
        # self.radioButton_rgb.toggled.connect(self.changeBackground)

    def init_pushbutton(self):
        self.pushButton_webcam.clicked.connect(self.run_webcam)
        self.pushButton_folder.clicked.connect(self.change_folder)
        self.pushButton_save.clicked.connect(self.save_current)
        self.pushButton_record.clicked.connect(self.record_video)
        self.pushButton_record.setEnabled(False)

    def init_slider(self):
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
        self.horizontalSlider_Body.sliderReleased.connect(self.change_body_threshold)
        self.horizontalSlider_Face.sliderReleased.connect(self.change_face_threshold)
        self.horizontalSlider_Hand.sliderReleased.connect(self.change_hand_threshold)

    def init_treeview(self):
        # 目录树
        self.treeView_file.setModel(self.tree_model)
        self.treeView_file.setRootIndex(self.tree_model.index(os.getcwd()))
        self.treeView_file.show()
        self.treeView_file.doubleClicked.connect(self.tree_clicked)

    def init_others(self):
        # 图像显示标签
        self.label_frame.setScaledContents(True)

    def show_frame(self):
        _, frame = self.cap.read()
        img = self.process_image(frame)
        if self.is_writing:
            self.count += 1
            cv2.imwrite(os.path.join(self.out_img_path.format(self.timestamp), "{:0>4d}.jpg".format(self.count)), img)
            if self.checkBox_body.isChecked():
                body = os.path.join(self.out_body_path.format(self.timestamp), "{:0>4d}_body.npy".format(self.count))
                np.save(body, self.datum.poseKeypoints)
            if self.checkBox_hand.isChecked():
                hand = os.path.join(self.out_hand_path.format(self.timestamp), "{:0>4d}_hand.npy".format(self.count))
                np.save(hand, self.datum.handKeypoints)
            if self.checkBox_face.isChecked():
                face = os.path.join(self.out_face_path.format(self.timestamp), "{:0>4d}_face.npy".format(self.count))
                np.save(face, self.datum.faceKeypoints)
            t = str(time.time() - self.start_time)[:4]
            cv2.putText(img, t, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        self.update_label(img)

    def tree_clicked(self, file_index):
        file_name = self.tree_model.filePath(file_index)
        if file_name.endswith(('.jpg', '.png')):
            if self.webcam_open:
                QMessageBox.information(self, "Note", "Please stop webcam first", QMessageBox.Yes)
                return
            img = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), -1)  # -1表示cv2.IMREAD_UNCHANGED
            print(img.shape)
            result = self.process_image(img)
            self.update_label(result)

    def update_label(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        h, w, c = frame.shape  # 获取图片形状
        image = QImage(frame, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label_frame.setPixmap(pixmap)

    def process_image(self, img):
        self.datum.cvInputData = img
        self.op_wrapper.emplaceAndPop([self.datum])
        result = self.datum.cvOutputData
        return result

    def change_background(self):
        if self.radioButton_black.isChecked():
            self.params['disable_blending'] = True
        else:
            self.params['disable_blending'] = False
        self.update_wrapper()

    def change_folder(self):
        folder_name = QFileDialog.getExistingDirectory(self, '标题', './')  # 可设置默认路径
        if folder_name:
            self.treeView_file.setRootIndex(self.tree_model.index(folder_name))
            self.treeView_file.show()

    def save_current(self):
        pixmap = self.label_frame.pixmap()
        if not pixmap:
            QMessageBox.warning(self, "Note", "No data in frame", QMessageBox.Yes)
            return
        body_keypoint = copy.deepcopy(self.datum.poseKeypoints) if self.checkBox_body.isChecked() else None
        hand_keypoint = copy.deepcopy(self.datum.handKeypoints) if self.checkBox_hand.isChecked() else None
        face_keypoint = copy.deepcopy(self.datum.faceKeypoints) if self.checkBox_face.isChecked() else None
        self.save_window.setFrame(pixmap.copy(), body_keypoint, hand_keypoint, face_keypoint)
        self.save_window.show()

    def record_video(self):
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Note", "Please open webcam first", QMessageBox.Yes)
            return

        if not self.is_writing:
            self.pushButton_webcam.setEnabled(False)
            self.pushButton_save.setEnabled(False)
            self.pushButton_folder.setEnabled(False)
            self.pushButton_record.setText("Stop Record")
            self.is_writing = True
            self.timestamp = str(int(time.time()))
            self.start_time = time.time()
            # 初始化路径
            if not os.path.exists(self.out_img_path.format(self.timestamp)):
                os.makedirs(self.out_img_path.format(self.timestamp))
            if not os.path.exists(self.out_body_path.format(self.timestamp)):
                os.makedirs(self.out_body_path.format(self.timestamp))
            if not os.path.exists(self.out_hand_path.format(self.timestamp)):
                os.makedirs(self.out_hand_path.format(self.timestamp))
            if not os.path.exists(self.out_face_path.format(self.timestamp)):
                os.makedirs(self.out_face_path.format(self.timestamp))
        else:
            self.pushButton_webcam.setEnabled(True)
            self.pushButton_save.setEnabled(True)
            self.pushButton_folder.setEnabled(True)
            self.pushButton_record.setText("Begin Record")
            self.is_writing = False

            QMessageBox.information(self, "Note", "Saving in {}".format(self.out_path), QMessageBox.Yes)
            self.timestamp = ""
            self.start_time = 0
            self.count = 0

    def run_webcam(self):
        if self.webcam_open:
            self.webcam_open = False
            self.cap.release()
            self.label_frame.clear()
            self.timer.stop()
            self.pushButton_webcam.setText("Open Webcam")
            self.pushButton_record.setEnabled(False)
        else:
            self.webcam_open = True
            self.cap.open(0)
            self.timer.start(20)
            self.pushButton_webcam.setText("Stop Webcam")
            self.pushButton_record.setEnabled(True)

    def check_body(self, status):
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.horizontalSlider_Body.setEnabled(flag)
        self.radioButton_black.setEnabled(flag)
        self.radioButton_rgb.setEnabled(flag)
        self.params["render_pose"] = render_pose
        self.update_wrapper()

    def check_hand(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Hand.setEnabled(flag)
        self.params["hand"] = flag
        self.update_wrapper()

    def check_face(self, status):
        flag = True if status == Qt.Checked else False
        self.horizontalSlider_Face.setEnabled(flag)
        self.params["face"] = flag
        self.update_wrapper()

    def change_body_threshold(self):
        value = self.horizontalSlider_Body.value()
        print(value)
        self.params["render_threshold"] = value / 100
        self.label_threshold_body.setText(str(value))
        self.update_wrapper()

    def change_hand_threshold(self):
        value = self.horizontalSlider_Hand.value()
        print(value)
        self.params["hand_render_threshold"] = value / 100
        self.label_threshold_hand.setText(str(value))
        self.update_wrapper()

    def change_face_threshold(self):
        value = self.horizontalSlider_Face.value()
        print(value)
        self.params["face_render_threshold"] = value / 100
        self.label_threshold_face.setText(str(value))
        self.update_wrapper()

    def update_wrapper(self):
        self.op_wrapper.configure(self.params)
        self.op_wrapper.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
