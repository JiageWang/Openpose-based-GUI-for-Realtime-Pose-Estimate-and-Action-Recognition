from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
import cv2


class LabelFrame(QLabel):
    def __init__(self, parent=None):
        super(LabelFrame, self).__init__(parent=parent)
        self.main_window = parent
        self.setAlignment(Qt.AlignCenter)  # 居中显示
        self.setMinimumSize(640, 480)
        self.setStyleSheet("background-color: rgb(0, 0, 0);")  # 黑底

    def update_frame(self, frame):
        pixmap = self.img_to_pixmap(frame)
        self.setPixmap(pixmap)
        self.resize_pix_map()

    def resize_pix_map(self):
        """保证图像等比例缩放"""
        pixmap = self.pixmap()
        if not pixmap:
            return
        if self.height() > self.width():
            width = self.width()
            height = int(pixmap.height() * (width / pixmap.width()))
        else:
            height = self.height()
            width = int(pixmap.width() * (height / pixmap.height()))
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)

    def resizeEvent(self, *args, **kwargs):
        self.resize_pix_map()

    @staticmethod
    def img_to_pixmap(frame):
        """nparray -> QPixmap"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        h, w, c = frame.shape  # 获取图片形状
        image = QImage(frame, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        return pixmap
