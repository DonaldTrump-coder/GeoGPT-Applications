from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty,pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush

#滑动按钮控件（选择是否需要人工辅助修改描述）
class SlideSwitch(QWidget):
    toggled=pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)

        self._checked = False
        self._thumb_pos = 2  # 滑块位置 (像素)
        self._animation = QPropertyAnimation(self, b"thumb_pos", self)
        self._animation.setDuration(200)

        self.clicked_callback = None

    def mousePressEvent(self, event):
        self.toggle()

    def toggle(self):
        self._checked = not self._checked
        start = self._thumb_pos
        end = self.width() - self.height() + 2 if self._checked else 2
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()
        self.toggled.emit(self._checked)

        if self.clicked_callback:
            self.clicked_callback(self._checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景
        bg_color = QColor("#00cc66") if self._checked else QColor("#cccccc")
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.height() / 2, self.height() / 2)

        # 滑块
        painter.setBrush(QBrush(QColor("#ffffff")))
        rect = QRectF(self._thumb_pos, 2, self.height() - 4, self.height() - 4)
        painter.drawEllipse(rect)

    def sizeHint(self):
        return self.size()

    # 属性：滑块位置（给动画用）
    def get_thumb_pos(self):
        return self._thumb_pos

    def set_thumb_pos(self, value):
        self._thumb_pos = value
        self.update()

    thumb_pos = pyqtProperty(float, get_thumb_pos, set_thumb_pos)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self.toggle()

    def onClicked(self, callback):
        self.clicked_callback = callback