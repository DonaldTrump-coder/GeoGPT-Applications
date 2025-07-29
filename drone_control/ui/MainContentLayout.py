from PyQt5 import QtWidgets,QtGui,QtCore,QtWebEngineWidgets

class MultiMediaDisplay(QtWidgets.QWidget):
    def __init__(self, url, parent = None):
        super().__init__(parent)

        self.container=QtWidgets.QWidget()
        self.container.setFixedSize(900, 600)
        self.container.setStyleSheet("background-color: black;")

        #实时视频展示框
        self.videodisplay=QtWidgets.QWidget(self.container)
        self.videodisplay.setFixedSize(900,600)
        self.videodisplay.setStyleSheet("color: black;background-color: black;")
        self.webview=QtWebEngineWidgets.QWebEngineView(self.videodisplay)
        self.webview.setUrl(QtCore.QUrl(url))
        weblayout=QtWidgets.QVBoxLayout(self.videodisplay)
        weblayout.setContentsMargins(0,0,0,0)
        weblayout.addWidget(self.webview)

        layout=QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)

        #图像展示框
        self.image1=QtWidgets.QLabel("前视", self.container)
        self.image1.setFixedSize(280, 160)
        self.image1.move(10,430)
        self.image1.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")
        self.image1.setAlignment(QtCore.Qt.AlignCenter)

        self.image2=QtWidgets.QLabel("后视", self.container)
        self.image2.setFixedSize(280, 160)
        self.image2.move(610,430)
        self.image2.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")
        self.image2.setAlignment(QtCore.Qt.AlignCenter)

        self.image3=QtWidgets.QLabel("左视")
        self.image4=QtWidgets.QLabel("俯视")
        self.image5=QtWidgets.QLabel("右视")
        for label in [self.image3, self.image4, self.image5]:
            label.setFixedSize(280, 160)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")

        image_row_layout = QtWidgets.QHBoxLayout()
        image_row_layout.setSpacing(10)
        image_row_layout.addWidget(self.image3)
        image_row_layout.addWidget(self.image4)
        image_row_layout.addWidget(self.image5)

        layout.addWidget(self.container)
        layout.addLayout(image_row_layout)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

    def show_captured_image(self,img_path):
        front_path=img_path+"_front.png"
        down_path=img_path+"_down.png"
        back_path=img_path+"_back.png"
        left_path=img_path+"_left.png"
        right_path=img_path+"_right.png"

        front_pix=QtGui.QPixmap(front_path).scaled(self.image1.size(), 
                              aspectRatioMode=QtCore.Qt.KeepAspectRatio, 
                              transformMode=QtCore.Qt.SmoothTransformation)
        down_pix=QtGui.QPixmap(down_path).scaled(self.image4.size(), 
                              aspectRatioMode=QtCore.Qt.KeepAspectRatio, 
                              transformMode=QtCore.Qt.SmoothTransformation)
        back_pix=QtGui.QPixmap(back_path).scaled(self.image2.size(), 
                              aspectRatioMode=QtCore.Qt.KeepAspectRatio, 
                              transformMode=QtCore.Qt.SmoothTransformation)
        left_pix=QtGui.QPixmap(left_path).scaled(self.image3.size(), 
                              aspectRatioMode=QtCore.Qt.KeepAspectRatio, 
                              transformMode=QtCore.Qt.SmoothTransformation)
        right_pix=QtGui.QPixmap(right_path).scaled(self.image5.size(), 
                              aspectRatioMode=QtCore.Qt.KeepAspectRatio, 
                              transformMode=QtCore.Qt.SmoothTransformation)
        
        self.image1.setPixmap(front_pix)
        self.image2.setPixmap(back_pix)
        self.image3.setPixmap(left_pix)
        self.image4.setPixmap(down_pix)
        self.image5.setPixmap(right_pix)

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

    #添加聊天信息（聊天文本以及是否为用户）
    def add_message(self,text,user):
        message=OneMessage(text,user)
        self.message_area.addWidget(message)
        QtCore.QTimer.singleShot(0, self.scroll_to_bottom)

    #滚动到底部
    def  scroll_to_bottom(self):
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

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
        

        if user == "VLM":
            layout.addStretch()
            layout.addWidget(text_label)
            layout.addWidget(avatar_label)

        elif user == "GeoGPT":
            layout.addWidget(avatar_label)
            layout.addWidget(text_label)
            layout.addStretch()

        else:
            layout.addStretch()
            layout.addWidget(text_label)
            layout.addWidget(avatar_label)

        self.setLayout(layout)

class MainContentLayout(QtWidgets.QWidget):
    def __init__(self, url, parent = None):
        super().__init__(parent)
        self.video_and_images=MultiMediaDisplay(url)
        self.chat=ChatDisplay()

        main_layout=QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.video_and_images)
        main_layout.addWidget(self.chat)
        main_layout.setContentsMargins(2, 2, 2, 2)