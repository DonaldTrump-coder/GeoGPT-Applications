from PyQt5 import QtGui, QtWidgets

#自定义标题栏
class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("无人机应急药物投送智能决策系统")
        font = QtGui.QFont("楷体", 18)
        self.label.setFont(font)
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.setFixedHeight(55)
        self.setStyleSheet("background-color: white; color: black;")
        self.layout.setContentsMargins(2,2,2,2)

        #增加右上角三个按钮控件
        self.btn_min = QtWidgets.QPushButton()
        self.btn_min.setIcon(QtGui.QIcon("icons/minimize-sign.png"))
        self.btn_min.setFixedSize(30, 30)
        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setIcon(QtGui.QIcon("icons/cross.png"))
        self.btn_close.setFixedSize(30, 30)
        self.btn_max_restore = QtWidgets.QPushButton()
        self.btn_max_restore.setIcon(QtGui.QIcon("icons/maximise.png"))
        self.btn_max_restore.setFixedSize(30, 30)