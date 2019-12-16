import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi


class FiletreeDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        loadUi("ui/dock_filetree.ui", self)

        self.selected_file = None
        self.curdir = os.path.abspath('.')

        self.fileSystemModel = QFileSystemModel()
        self.dock_label = QLabel("Current Directory")
        self.dock_label.setMinimumHeight(30)
        self.dock_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setTitleBarWidget(self.dock_label)
        self.init_treeview()

        self.treeView.doubleClicked.connect(self.read_file)
        self.pushButton_folder.clicked.connect(self.load_folder)
        self.pushButton_goto.clicked.connect(self.goto_folder)
        self.pushButton_pardir.clicked.connect(self.parent_folder)

        self.hide()

    def init_treeview(self):
        self.fileSystemModel.setRootPath('.')
        self.treeView.setModel(self.fileSystemModel)
        self.treeView.setRootIndex(self.fileSystemModel.index(self.curdir))
        # 隐藏size,date等列
        self.treeView.setColumnWidth(0, 200)
        self.treeView.setColumnHidden(1, True)
        self.treeView.setColumnHidden(2, True)
        self.treeView.setColumnHidden(3, True)
        # 不显示标题栏
        self.treeView.header().hide()
        # 设置动画
        self.treeView.setAnimated(True)
        # 选中不显示虚线
        self.treeView.setFocusPolicy(Qt.NoFocus)
        self.treeView.setMinimumWidth(200)
        self.lineEdit_current.setText(os.path.abspath('.'))

    def change_folder(self, new_folder):
        self.curdir = new_folder
        self.lineEdit_current.setText(new_folder)
        self.treeView.setRootIndex(self.fileSystemModel.index(new_folder))
        self.show()

    def parent_folder(self):
        new_folder = os.path.dirname(self.curdir)
        self.change_folder(new_folder)

    def load_folder(self):
        new_folder = QFileDialog.getExistingDirectory(self, '请选择目录', './')  # 可设置默认路径
        if not new_folder:
            return
        self.change_folder(new_folder)

    def goto_folder(self):
        new_foler = self.lineEdit_current.text()
        if not os.path.exists(new_foler):
            QMessageBox.about(self.parent(), u'提示', u"目录不存在")
            return
        self.change_folder(new_foler)

    def read_file(self, file_index):
        file = self.fileSystemModel.filePath(file_index)
        if not file:
            return False
        elif file.endswith((".jpg", ".png", ".JPG", ".PNG")):
            self.selected_file = file
            self.parent().run_image(file)
        elif file.endswith((".avi", ".mp4")):
            self.selected_file = file
            self.parent().run_video(file)
