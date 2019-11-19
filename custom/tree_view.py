from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeView, QDockWidget, QFileSystemModel


class FileSystemTreeView(QTreeView, QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main_window = parent
        self.fileSystemModel = QFileSystemModel()
        self.fileSystemModel.setRootPath('.')
        self.setModel(self.fileSystemModel)
        self.setRootIndex(self.fileSystemModel.index('.'))
        # 隐藏size,date等列
        self.setColumnWidth(0, 200)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        # 不显示标题栏
        self.header().hide()
        # 设置动画
        self.setAnimated(True)
        # 选中不显示虚线
        self.setFocusPolicy(Qt.NoFocus)
        self.setMinimumWidth(200)

    def alter_dir(self, path):
        self.setRootIndex(self.fileSystemModel.index(path))
        self.show()
