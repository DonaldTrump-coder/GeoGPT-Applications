from PyQt5 import QtWidgets,QtGui,QtCore

class MultiMediaDisplay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.videodisplay=QtWidgets.QLabel("第三人称视频展示")
        self.videodisplay.setFixedSize(900,750)
        self.videodisplay.setStyleSheet("background-color: black;")
        self.layout=QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.videodisplay)
        self.layout.setContentsMargins(2,2,2,2)

#聊天区域
class ChatDisplay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.chatlabel=QtWidgets.QLabel("聊天区")
        self.chatlabel.setStyleSheet("background-color: gray;")

        self.messagedisplay=MessageDisplay()

        self.layout=QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.chatlabel)
        self.layout.addWidget(self.messagedisplay)
        self.layout.setContentsMargins(2,2,2,2)

class MessageDisplay(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_area=QtWidgets.QVBoxLayout()
        self.message_area.setAlignment(QtCore.Qt.AlignTop)
        container=QtWidgets.QWidget()
        container.setLayout(self.message_area)
        self.setWidgetResizable(True)
        self.setWidget(container)

class MainContentLayout(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.video_and_images=MultiMediaDisplay()
        self.chat=ChatDisplay()

        main_layout=QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.video_and_images)
        main_layout.addWidget(self.chat)
        main_layout.setContentsMargins(2, 2, 2, 2)