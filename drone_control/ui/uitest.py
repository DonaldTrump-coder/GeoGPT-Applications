from dronetask_display import Drone_Window
import sys
from PyQt5 import QtWidgets,QtCore
import time

stream_url="http://127.0.0.1"

app=QtWidgets.QApplication(sys.argv)
window=Drone_Window(url=stream_url)
window.show()
sys.exit(app.exec_())