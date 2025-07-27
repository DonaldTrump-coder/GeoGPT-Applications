from PyQt5 import QtWidgets,QtGui

class MultiMediaDisplay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.videodisplay=QtWidgets.QLabel("第三人称视频展示")
        self.videodisplay.setFixedSize(900,750)
        self.videodisplay.setStyleSheet("background-color: black;")
        self.layout=QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.videodisplay)

class ChatDisplay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.chat=QtWidgets.QLabel("聊天区")
        self.chat.setStyleSheet("background-color: gray;")
        self.layout=QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.chat)

class MainContentLayout(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.video_and_images=MultiMediaDisplay(self)
        self.chat=ChatDisplay(self)

        main_layout=QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.video_and_images)
        main_layout.addWidget(self.chat)