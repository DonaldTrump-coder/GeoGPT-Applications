from PyQt5 import QtWidgets,QtGui,QtCore,QtWebEngineWidgets
from SlideSwitch import SlideSwitch

class MultiMediaDisplay(QtWidgets.QWidget):
    def __init__(self, url, parent = None):
        super().__init__(parent)

        self.container=QtWidgets.QWidget()
        self.container.setStyleSheet("background-color: black;")

        #实时视频展示框
        self.videodisplay=QtWidgets.QWidget(self.container)
        self.videodisplay.setStyleSheet("color: white;background-color: white;")
        self.webview=QtWebEngineWidgets.QWebEngineView()
        self.webview.setUrl(QtCore.QUrl(url))
        weblayout=QtWidgets.QVBoxLayout(self.videodisplay)
        weblayout.setContentsMargins(0,0,0,0)
        weblayout.addWidget(self.webview)

        layout=QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)

        #图像展示框
        self.image_widget1=QtWidgets.QWidget(self.container)
        self.image_widget1.setStyleSheet("background: white; border: 2px solid #888888; border-radius: 10px;")
        image_layout1=QtWidgets.QVBoxLayout(self.image_widget1)
        label1=QtWidgets.QLabel("前视")
        label1.setAlignment(QtCore.Qt.AlignCenter)
        label1.setStyleSheet("font-size: 18px; font-family: 楷体")
        image_layout1.addWidget(label1)
        self.image1=QtWidgets.QLabel()
        image_layout1.addWidget(self.image1)
        self.image1.setFixedSize(280, 160)
        self.image_widget1.move(int(self.container.width()*0.02),
                                int(self.container.height()*0.60)
                                )
        self.image1.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")
        self.image1.setAlignment(QtCore.Qt.AlignCenter)

        self.image_widget2=QtWidgets.QWidget(self.container)
        self.image_widget2.setStyleSheet("background: white; border: 2px solid #888888; border-radius: 10px;")
        image_layout2=QtWidgets.QVBoxLayout(self.image_widget2)
        label2=QtWidgets.QLabel("后视")
        label2.setAlignment(QtCore.Qt.AlignCenter)
        label2.setStyleSheet("font-size: 18px; font-family: 楷体")
        image_layout2.addWidget(label2)
        self.image2=QtWidgets.QLabel()
        image_layout2.addWidget(self.image2)
        self.image2.setFixedSize(280, 160)
        self.image_widget2.move(int(self.container.width()),
                                int(self.container.height()*0.60)
                                )
        self.image2.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")
        self.image2.setAlignment(QtCore.Qt.AlignCenter)

        self.image_widget3=QtWidgets.QWidget()
        self.image_widget3.setStyleSheet("background: white; border: 2px solid #888888; border-radius: 10px;")
        image_layout3=QtWidgets.QVBoxLayout(self.image_widget3)
        label3=QtWidgets.QLabel("左视")
        label3.setAlignment(QtCore.Qt.AlignCenter)
        label3.setStyleSheet("font-size: 18px; font-family: 楷体; color:black;")
        image_layout3.addWidget(label3,1)
        self.image3=QtWidgets.QLabel()
        image_layout3.addWidget(self.image3,10)

        self.image_widget4=QtWidgets.QWidget()
        self.image_widget4.setStyleSheet("background: white; border: 2px solid #888888; border-radius: 10px;")
        image_layout4=QtWidgets.QVBoxLayout(self.image_widget4)
        label4=QtWidgets.QLabel("俯视")
        label4.setAlignment(QtCore.Qt.AlignCenter)
        label4.setStyleSheet("font-size: 18px; font-family: 楷体; color:black;")
        image_layout4.addWidget(label4,1)
        self.image4=QtWidgets.QLabel()
        image_layout4.addWidget(self.image4,10)

        self.image_widget5=QtWidgets.QWidget()
        self.image_widget5.setStyleSheet("background: white; border: 2px solid #888888; border-radius: 10px;")
        image_layout5=QtWidgets.QVBoxLayout(self.image_widget5)
        label5=QtWidgets.QLabel("右视")
        label5.setAlignment(QtCore.Qt.AlignCenter)
        label5.setStyleSheet("font-size: 18px; font-family: 楷体; color:black;")
        image_layout5.addWidget(label5,1)
        self.image5=QtWidgets.QLabel()
        image_layout5.addWidget(self.image5,10)

        for label in [self.image3, self.image4, self.image5]:
            label.setFixedSize(280, 160)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("background-color: #222; color: white; border: 1px solid #555;")

        self.switch=SlideSwitch(self.container)
        self.switch.move(840, 100)
        self.switch_label=QtWidgets.QLabel("辅助描述",self.container)
        self.switch_label.setGeometry(740, 98, 100, 30)
        self.switch_label.setStyleSheet("color: black; font-family: 黑体; font-size:22px; background: transparent;")

        self.images_widget=QtWidgets.QWidget()
        image_row_layout = QtWidgets.QHBoxLayout(self.images_widget)
        image_row_layout.setSpacing(10)
        image_row_layout.addWidget(self.image_widget3)
        image_row_layout.addWidget(self.image_widget4)
        image_row_layout.addWidget(self.image_widget5)

        layout.addWidget(self.container,9)
        layout.addWidget(self.images_widget,2)
        layout.setContentsMargins(1,1,1,1)
        layout.setSpacing(5)

    def resizeEvent(self, event):
        # 设置 videodisplay 和 webview 的大小为 container 的大小
        container_size = self.container.size()
        self.videodisplay.setGeometry(0, 0, container_size.width(), container_size.height())
        self.webview.setGeometry(0, 0, container_size.width(), container_size.height())
        super().resizeEvent(event)

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
        self.chatlabel=QtWidgets.QLabel("智能体聊天区")
        self.chatlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.chatlabel.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,stop: 0 #7aaaff, stop: 1 #a3c1ff); border-radius: 10px; color: #002244; font-size: 24px; font-weight: bold; font-family: 微软雅黑;")

        self.messagedisplay=MessageDisplay()
        self.input_box=QtWidgets.QTextEdit()
        
        self.input_box.setEnabled(False)
        self.send_button=QtWidgets.QPushButton("发送")
        self.send_button.setFixedHeight(40)
        self.send_button.setStyleSheet("QPushButton{background-color: #ffb6c1;border: 2px solid #ff69b4;border-radius: 18px;color: white;font-weight: bold;font-size: 16px;font-family: 微软雅黑; padding: 6px 12px;} QPushButton:hover {background-color: #ffa6c9;}QPushButton:pressed {background-color: #ff69b4;}")

        input_layout=QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        self.input_widget=QtWidgets.QWidget()
        self.input_widget.setLayout(input_layout)

        layout=QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.chatlabel,2)
        layout.addWidget(self.messagedisplay,18)
        layout.addWidget(self.input_widget,3)
        self.input_box.setFixedHeight(70)
        layout.setContentsMargins(3,3,3,3)

    def send_descriptions(self,text):
        self.input_box.setText(text)
        self.input_box.setEnabled(True)

class MessageDisplay(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_area=QtWidgets.QVBoxLayout()
        self.message_area.setAlignment(QtCore.Qt.AlignTop)
        container=QtWidgets.QWidget()
        container.setLayout(self.message_area)
        self.setWidgetResizable(True)
        self.setWidget(container)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

    #添加聊天信息（聊天文本以及是否为用户）
    def add_message(self,text,user):
        message=OneMessage(text,user,self.width()*0.7)
        self.message_area.addWidget(message)
        QtCore.QTimer.singleShot(0, self.scroll_to_bottom)

    #滚动到底部
    def scroll_to_bottom(self):
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

#消息组件（头像+信息内容）
class OneMessage(QtWidgets.QWidget):
    def __init__(self, text, user, max_width, parent = None):
        super().__init__(parent)
        layout=QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(10)

        GPT_label = QtWidgets.QLabel()
        GPT_label.setPixmap(QtGui.QPixmap("ui/icons/artificial-intelligence.png").scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        user_label = QtWidgets.QLabel()
        user_label.setPixmap(QtGui.QPixmap("ui/icons/user.png").scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        VLM_label = QtWidgets.QLabel()
        VLM_label.setPixmap(QtGui.QPixmap("ui/icons/zoom.png").scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        text_widget=QtWidgets.QWidget()
        widget_layout=QtWidgets.QVBoxLayout(text_widget)
        name_label=QtWidgets.QLabel()
        name_label.setStyleSheet("color: #555555; font-family: Consolas; font-size: 16px;")
        text_label = QtWidgets.QTextBrowser()
        text_label.setText(text)

        text_label.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        text_label.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        text_label.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        text_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        text_label.setReadOnly(True)  # 只读，不允许编辑
        text_label.document().setTextWidth(int(max_width*0.6))
        height = int(text_label.document().size().height()) + 25  # +5是为了留点边距
        text_label.setFixedHeight(height)

        #text_label.setWordWrap(True)
        text_label.setMaximumWidth(int(max_width))
        widget_layout.addWidget(name_label)
        widget_layout.addWidget(text_label)

        if user == "VLM":
            name_label.setText("VLM")
            widget_layout.setAlignment(QtCore.Qt.AlignRight)
            text_label.setStyleSheet("color:#000000; font-family: Arial; font-size: 18px;background-color: #d0f0ff; padding: 8px 12px;border-radius: 12px;")
            name_label.setAlignment(QtCore.Qt.AlignRight)
            layout.addStretch()
            layout.addWidget(text_widget)
            layout.addWidget(VLM_label)

        elif user == "GeoGPT":
            name_label.setText("GeoGPT")
            name_label.setAlignment(QtCore.Qt.AlignLeft)
            text_label.setStyleSheet("color:#000000; font-family: Arial; font-size: 18px;background-color: #f0f0f0; padding: 8px 12px;border-radius: 12px;")
            layout.addWidget(GPT_label)
            layout.addWidget(text_widget)
            layout.addStretch()

        else:
            name_label.setText("user")
            name_label.setAlignment(QtCore.Qt.AlignRight)
            widget_layout.setAlignment(QtCore.Qt.AlignRight)
            text_label.setStyleSheet("color:#000000; font-family: Arial; font-size: 18px;background-color: #b9f6ca; padding: 8px 12px;border-radius: 12px;")
            layout.addStretch()
            layout.addWidget(text_widget)
            layout.addWidget(user_label)

        self.setLayout(layout)

class MainContentLayout(QtWidgets.QWidget):
    def __init__(self, url, parent = None):
        super().__init__(parent)
        self.video_and_images=MultiMediaDisplay(url)
        self.chat=ChatDisplay()

        main_layout=QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.video_and_images,5)
        main_layout.addWidget(self.chat,2)
        main_layout.setContentsMargins(2,2,2,2)