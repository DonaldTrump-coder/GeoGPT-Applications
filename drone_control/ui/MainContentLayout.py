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
        self.input_box=QtWidgets.QTextEdit()
        self.input_box.setFixedHeight(30)
        self.send_button=QtWidgets.QPushButton("发送")

        self.input_layout=QtWidgets.QHBoxLayout()
        self.input_layout.addWidget(self.input_box)
        self.input_layout.addWidget(self.send_button)

        self.layout=QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.chatlabel)
        self.layout.addWidget(self.messagedisplay)
        self.layout.addLayout(self.input_layout)
        self.layout.setContentsMargins(3,3,3,3)

class MessageDisplay(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_area=QtWidgets.QVBoxLayout()
        self.message_area.setAlignment(QtCore.Qt.AlignTop)
        container=QtWidgets.QWidget()
        container.setLayout(self.message_area)
        self.setWidgetResizable(True)
        self.setWidget(container)

        self.add_message("你好，欢迎来到聊天室！")
        self.add_message("你好，我是用户！")

    #添加聊天信息（聊天文本以及是否为用户）
    def add_message(self,text,user):
        message=OneMessage(text,user)
        self.message_area.addWidget(message)

#消息组件（头像+信息内容）
class OneMessage(QtWidgets.QWidget):
    def __init__(self, text, user,parent = None):
        super().__init__(parent)
        layout=QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(10)

        avatar_label = QtWidgets.QLabel()
        avatar_label.setPixmap(QtGui.QPixmap("icons/artificial-intelligence.png").scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        text_label = QtWidgets.QLabel(text)
        text_label.setWordWrap(True)
        

        if user is "VLM":
            layout.addStretch()
            layout.addWidget(text_label)
            layout.addWidget(avatar_label)

        elif user is "GeoGPT":
            layout.addWidget(avatar_label)
            layout.addWidget(text_label)
            layout.addStretch()

        else:
            layout.addStretch()
            layout.addWidget(text_label)
            layout.addWidget(avatar_label)

        self.setLayout(layout)

class MainContentLayout(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.video_and_images=MultiMediaDisplay()
        self.chat=ChatDisplay()

        main_layout=QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.video_and_images)
        main_layout.addWidget(self.chat)
        main_layout.setContentsMargins(2, 2, 2, 2)