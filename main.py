import os
import sys
import cv2
import copy
import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QLabel, \
    QStatusBar, QMenuBar, QAction, QToolBar, QApplication

from custom.camera import Camera
from custom.label_frame import LabelFrame
from custom.tree_view import FileSystemTreeView
from custom.setting_widget import SettingWidget
from custom.openpose_model import OpenposeModel
from custom.save_widget import SaveWidget
from custom.gesture_model import GestureModel
from custom.media_control import MediaControl

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


class OpenposeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpencvGUI")
        self.setWindowIcon(QIcon("icon/logo.png"))

        # QAction
        self.action_autosave = QAction(QIcon("icon/autosave.png"), "自动保存", self)
        self.action_save = QAction(QIcon("icon/save.png"), "保存", self)
        self.action_image = QAction(QIcon("icon/image.png"), "打开图片", self)
        self.action_video = QAction(QIcon("icon/video.png"), "打开视频", self)
        self.action_camera = QAction(QIcon("icon/camera.png"), "打开摄像头", self)
        self.action_folder = QAction(QIcon("icon/folder.png"), "打开文件夹", self)
        self.action_setting = QAction(QIcon("icon/setting.png"), "设置", self)
        self.action_filetree = QAction(QIcon("icon/filetree.png"), "目录树", self)
        self.action_camera.setCheckable(True)
        self.action_video.setCheckable(True)
        self.action_setting.setCheckable(True)
        self.action_filetree.setCheckable(True)
        self.action_autosave.setCheckable(True)

        # 菜单栏
        self.menu_bar = QMenuBar()
        self.menu_open = self.menu_bar.addMenu("Open")
        self.menu_open.addAction(self.action_image)
        self.menu_open.addAction(self.action_video)
        self.menu_open.addAction(self.action_camera)

        self.menu_view = self.menu_bar.addMenu("View")
        self.menu_view.addAction(self.action_setting)
        self.menu_view.addAction(self.action_filetree)

        self.menu_function = self.menu_bar.addMenu("Function")
        self.action_background = self.menu_function.addAction("Black/RGB Blackground")
        self.action_geture = self.menu_function.addAction("Gesture Recognition")

        self.setMenuBar(self.menu_bar)

        # 工具栏
        self.tool_bar = QToolBar()
        self.tool_bar.addAction(self.action_save)
        self.tool_bar.addAction(self.action_autosave)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_folder)
        self.tool_bar.addAction(self.action_camera)
        self.tool_bar.addAction(self.action_image)
        self.tool_bar.addAction(self.action_video)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_setting)
        self.tool_bar.addAction(self.action_filetree)
        self.addToolBar(self.tool_bar)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_fps = QLabel("FPS:00.0")
        self.status_bar.addPermanentWidget(self.status_fps)
        self.setStatusBar(self.status_bar)

        # 组件
        self.timer = QTimer()
        self.camera = Camera(self)
        self.setting_widget = SettingWidget(self)
        self.label_frame = LabelFrame(self)
        self.file_system_tree = FileSystemTreeView(self)
        self.openpose_model = OpenposeModel(self)
        self.media_control = MediaControl(self)
        self.save_widget = SaveWidget()
        self.gesture_model = GestureModel()

        # 设置dock
        self.dock_filetree = QDockWidget(self)
        self.dock_filetree.setWidget(self.file_system_tree)
        self.dock_file_label = QLabel("Current Directory")
        self.dock_file_label.setMinimumHeight(25)
        self.dock_file_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.dock_filetree.setTitleBarWidget(self.dock_file_label)
        self.dock_filetree.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.dock_filetree.hide()

        self.dock_setting = QDockWidget(self)
        self.dock_setting.setWidget(self.setting_widget)
        self.dock_setting_label = QLabel("Openpose Settings")
        self.dock_setting_label.setMinimumHeight(25)
        self.dock_setting_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.dock_setting.setTitleBarWidget(self.dock_setting_label)
        self.dock_setting.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.dock_setting.hide()

        self.dock_media = QDockWidget(self)
        self.dock_media.setWidget(self.media_control)
        self.dock_media.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_media.hide()

        self.setCentralWidget(self.label_frame)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_setting)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_filetree)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_media)

        # 信号与槽

        self.setting_widget.horizontalSlider_Body.sliderReleased.connect(self.change_body_threshold)
        self.setting_widget.horizontalSlider_Face.sliderReleased.connect(self.change_face_threshold)
        self.setting_widget.horizontalSlider_Hand.sliderReleased.connect(self.change_hand_threshold)
        self.setting_widget.checkBox_body.stateChanged.connect(
            self.check_body)  # 状态改变触发check_box_changed函数
        self.setting_widget.checkBox_hand.stateChanged.connect(
            self.check_hand)  # 状态改变触发check_box_changed函数
        self.setting_widget.checkBox_face.stateChanged.connect(
            self.check_face)  # 状态改变触发check_box_changed函数
        self.setting_widget.radioButton_black.toggled.connect(self.change_background)

        self.setting_widget.comboBox_resolution.currentIndexChanged.connect(self.change_resolution)

        self.media_control.play_button.toggled.connect(self.play_media)

        self.action_image.triggered.connect(self.open_image)
        self.action_video.triggered.connect(self.open_video)
        self.action_folder.triggered.connect(self.open_folder)
        self.action_camera.triggered.connect(self.open_camera)
        self.action_filetree.triggered.connect(self.show_filetree)
        self.action_setting.triggered.connect(self.show_setting)
        self.action_autosave.triggered.connect(self.auto_save)

        self.action_save.triggered.connect(self.save_current)
        self.action_setting.triggered.connect(self.setting_widget.show)

        self.file_system_tree.doubleClicked.connect(self.open_image)
        self.camera.timer.timeout.connect(self.update)
        self.timer.timeout.connect(self.save_current)

    def update(self):
        start_time = time.time()
        frame = self.camera.frame()
        self.media_control.update(self.camera.frame_pos, self.camera.frame_count)
        if frame is None:
            return None
        result, keypoints = self.openpose_model(frame)
        result, keypoints = self.gesture_recognition(result, keypoints)

        message = self.generate_message(keypoints)
        self.label_frame.update_frame(result)
        fps = 1 / (time.time() - start_time)
        self.status_fps.setText("FPS:{:.1f}".format(fps))
        self.status_bar.showMessage(message, 2000)
        return result, keypoints

    def gesture_recognition(self, result, keypoints):
        """实现手势识别"""
        if self.setting_widget.gesture_on():
            hands = keypoints[1]
            person_num = hands[0].shape[0]
            for i in range(person_num):
                for hand in hands:
                    rect = self.gesture_model.hand_bbox(hand[i])
                    gesture = self.gesture_model(hand[i])
                    if rect:
                        print(rect)
                        x, y, w, h = rect
                        cv2.rectangle(result, (x, y), (x + w, y + h), (255, 255, 255))
                        cv2.putText(result, gesture, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        return result, keypoints

    def generate_message(self, keypoints):
        """获取识别结果信息"""
        if keypoints[0].size != 1:
            person_num = keypoints[0].shape[0]
            message = "person: {}".format(person_num)
            for i in range(person_num):
                message += " | person{}(".format(i + 1)
                if self.setting_widget.body_on():
                    pose_keypoints = keypoints[0][i, :, 2]
                    pose_detected = pose_keypoints[pose_keypoints > self.setting_widget.body_threshold()]
                    message += "pose: {:>2d}/{}".format(pose_detected.size, 25)

                if self.setting_widget.hand_on():
                    right_hand_keypoinys = keypoints[1][0][i, :, 2]
                    left_hand_keypoinys = keypoints[1][1][i, :, 2]

                    right_hand_detected = right_hand_keypoinys[
                        right_hand_keypoinys > self.setting_widget.hand_threshold()]
                    left_hand_detected = left_hand_keypoinys[left_hand_keypoinys > self.setting_widget.hand_threshold()]
                    message += " | right hand: {:>2d}/{}".format(right_hand_detected.size, 21)
                    message += " | left hand: {:>2d}/{}".format(left_hand_detected.size, 21)
                message += ")"
        else:
            message = "person: {}".format(0)
        return message

    def save_current(self):
        if not self.label_frame.pixmap():
            QMessageBox.warning(self, "Note", "No data in frame", QMessageBox.Yes)
            return

        pixmap = self.label_frame.cvimg2pixmap(self.openpose_model.get_rendered_image())
        body_keypoints, hand_keypoints, face_keypoints = self.openpose_model.get_keypoints()
        body_keypoints = copy.deepcopy(body_keypoints) if self.setting_widget.body_on() else None
        hand_keypoints = copy.deepcopy(hand_keypoints) if self.setting_widget.hand_on() else None
        face_keypoints = copy.deepcopy(face_keypoints) if self.setting_widget.face_on() else None
        keypoints = (body_keypoints, hand_keypoints, face_keypoints)

        if self.timer.isActive():
            self.save_widget.save(pixmap.copy(), *keypoints)
        else:
            message = self.generate_message(keypoints)
            self.save_widget.setFrame(pixmap.copy(), *keypoints, message)
            self.save_widget.show()

    def auto_save(self):
        if not self.camera.is_open():
            self.action_autosave.setChecked(False)
        if self.action_autosave.isChecked():
            self.timer.start(self.setting_widget.save_interval() * 1000)
        else:
            self.timer.stop()

    def update_setting(self):
        pass

    def update_openpose(self, key, value):
        pass

    # 槽函数

    # 参数
    def check_body(self, status):
        # 姿态估计
        flag = True if status == Qt.Checked else False
        render_pose = 1 if status == Qt.Checked else 0
        self.setting_widget.horizontalSlider_Body.setEnabled(flag)
        self.setting_widget.radioButton_black.setEnabled(flag)
        self.setting_widget.radioButton_rgb.setEnabled(flag)
        self.openpose_model.update_wrapper("render_pose", render_pose)

    def check_hand(self, status):
        # 手部估计
        flag = True if status == Qt.Checked else False
        self.setting_widget.horizontalSlider_Hand.setEnabled(flag)
        self.setting_widget.checkBox_gesture.setEnabled(flag)
        self.openpose_model.update_wrapper("hand", flag)

    def check_face(self, status):
        # 脸部估计
        flag = True if status == Qt.Checked else False
        self.setting_widget.horizontalSlider_Face.setEnabled(flag)
        self.setting_widget.checkBox_emotion.setEnabled(flag)
        self.openpose_model.update_wrapper("face", flag)

    def change_body_threshold(self):
        # 姿态估计阈值
        value = self.setting_widget.body_threshold()
        self.setting_widget.label_threshold_body.setText(str(value * 100))
        self.openpose_model.update_wrapper("render_threshold", value)

    def change_hand_threshold(self):
        # 手部估计阈值
        value = self.setting_widget.hand_threshold()
        self.setting_widget.label_threshold_hand.setText(str(value * 100))
        self.openpose_model.update_wrapper("hand_render_threshold", value)

    def change_face_threshold(self):
        # 脸部估计阈值
        value = self.setting_widget.face_threshold()
        self.setting_widget.label_threshold_face.setText(str(value * 100))
        self.openpose_model.update_wrapper("face_render_threshold", value)

    def change_resolution(self):
        resolution = self.setting_widget.net_resolution()
        self.openpose_model.update_wrapper("net_resolution", resolution)

    def change_background(self):
        # 背景
        self.openpose_model.update_wrapper("disable_blending", self.setting_widget.black_background())

    # 功能
    def show_setting(self):
        if self.dock_setting.isHidden():
            self.dock_setting.show()
        else:
            self.dock_setting.hide()

    def show_filetree(self):
        if self.dock_filetree.isHidden():
            self.dock_filetree.show()
        else:
            self.dock_filetree.hide()

    def open_image(self, file_index=None):
        if file_index:
            file = self.file_system_tree.fileSystemModel.filePath(file_index)
        else:
            file, _ = QFileDialog.getOpenFileName(self, '请选择图片', './',
                                                  'Image files(*.jpg *.png *.JPG *.PNG)')  # 可设置默认路径
        if not file or not file.endswith((".jpg", ".png", ".JPG", ".PNG")):
            return False
        image = cv2.imread(file)
        result, keypoints = self.openpose_model(image)
        message = self.generate_message(keypoints)
        # self.label_frame.resize(*image.shape[:2])
        self.label_frame.update_frame(result)
        self.status_bar.showMessage(message)

    def open_video(self):
        if self.action_video.isChecked():
            file, _ = QFileDialog.getOpenFileName(self, '请选择视频', './', 'Video files(*.mp4 *.avi)')  # 可设置默认路径
            if not file:
                self.action_video.setChecked(False)
                return
            self.camera.start(file)
            self.label_frame.resize(*self.camera.resolution)
            self.action_video.setIcon(QIcon('icon/stop.png'))
            self.update()  # 初始化画面
            self.camera.is_pause = True
            self.media_control.pause()
            self.dock_media.show()
        else:
            self.label_frame.clear()
            self.camera.stop()
            self.status_fps.setText("FPS:00.0")
            self.action_video.setIcon(QIcon("icon/video.png"))
            self.media_control.play()
            self.dock_media.hide()

    def open_folder(self):
        new_foler = QFileDialog.getExistingDirectory(self, '请选择目录', './')  # 可设置默认路径
        if not new_foler:
            return
        self.file_system_tree.alter_dir(new_foler)
        self.dock_filetree.show()
        self.status_bar.showMessage("current folder: {}".format(new_foler), 3000)

    def open_camera(self):
        if self.action_camera.isChecked():
            self.camera.start()
            self.action_camera.setIcon(QIcon('icon/stop.png'))
        else:
            self.label_frame.clear()
            self.camera.stop()
            self.status_fps.setText("FPS:00.0")
            self.action_camera.setIcon(QIcon("icon/camera.png"))

    def play_media(self):
        if not self.media_control.is_play():
            self.media_control.pause()
            self.camera.is_pause = True
        else:
            self.media_control.play()
            self.camera.is_pause = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenposeGUI()
    window.show()
    sys.exit(app.exec_())
