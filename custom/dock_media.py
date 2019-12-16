from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.uic import loadUi


class MediaDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        loadUi("ui/dock_media.ui", self)
        self.dock_label = QLabel("Media control")
        self.dock_label.setMinimumHeight(25)
        self.dock_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setTitleBarWidget(self.dock_label)

        self.play_button.toggled.connect(self.play_media)
        self.replay_button.clicked.connect(self.replay_media)

        self.hide()

    def play_media(self):
        if self.is_play:
            self.parent().camera.begin()
        else:
            self.parent().camera.pause()

    def replay_media(self):
        self.parent().camera.restart()
        self.parent().update_frame()
        if not self.is_play:
            self.parent().camera.pause()

    def update_slider(self, pos, frames):
        self.process_slider.setMaximum(frames)
        self.process_slider.setValue(pos)

    def reset(self):
        self.play_button.setChecked(False)
        self.process_slider.setValue(0)

    @property
    def frame_pos(self):
        return self.process_slider.value()

    @property
    def is_play(self):
        return self.play_button.isChecked()
