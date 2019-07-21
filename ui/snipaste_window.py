# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'snipaste_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Snipaste(object):
    def setupUi(self, Snipaste):
        Snipaste.setObjectName("Snipaste")
        Snipaste.resize(658, 533)
        self.verticalLayout = QtWidgets.QVBoxLayout(Snipaste)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_frame = QtWidgets.QLabel(Snipaste)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_frame.sizePolicy().hasHeightForWidth())
        self.label_frame.setSizePolicy(sizePolicy)
        self.label_frame.setMinimumSize(QtCore.QSize(640, 480))
        self.label_frame.setMaximumSize(QtCore.QSize(640, 480))
        self.label_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.label_frame.setObjectName("label_frame")
        self.verticalLayout.addWidget(self.label_frame)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_save = QtWidgets.QPushButton(Snipaste)
        self.pushButton_save.setObjectName("pushButton_save")
        self.horizontalLayout.addWidget(self.pushButton_save)
        self.pushButton_cancel = QtWidgets.QPushButton(Snipaste)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Snipaste)
        QtCore.QMetaObject.connectSlotsByName(Snipaste)

    def retranslateUi(self, Snipaste):
        _translate = QtCore.QCoreApplication.translate
        Snipaste.setWindowTitle(_translate("Snipaste", "Form"))
        self.label_frame.setText(_translate("Snipaste", "TextLabel"))
        self.pushButton_save.setText(_translate("Snipaste", "Save"))
        self.pushButton_cancel.setText(_translate("Snipaste", "Cancel"))

