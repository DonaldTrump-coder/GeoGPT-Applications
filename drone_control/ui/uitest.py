from dronetask_display import Drone_Window
import sys
from PyQt5 import QtWidgets,QtCore
import time

stream_url="http://127.0.0.1"

app=QtWidgets.QApplication(sys.argv)
window=Drone_Window(url=stream_url)
window.content.chat.messagedisplay.add_message('123','VLM')
window.content.chat.messagedisplay.add_message('yes','user')
window.content.chat.messagedisplay.add_message('no','GeoGPT')
window.show()
sys.exit(app.exec_())