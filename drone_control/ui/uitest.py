from dronetask_display import Drone_Window
import sys
from PyQt5 import QtWidgets,QtCore
import time

stream_url="http://127.0.0.1"

app=QtWidgets.QApplication(sys.argv)
window=Drone_Window(url=stream_url)
window.content.chat.messagedisplay.add_message('我和我的祖国，一刻也不能分割，无论我走到哪里，都流出一首赞歌，我歌唱每一座高山，我歌唱每一条河，袅袅炊烟，小小村落','VLM')
window.content.chat.messagedisplay.add_message('qqq11111111111111111111111yes','user')
window.content.chat.messagedisplay.add_message('1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111no','GeoGPT')
window.show()
sys.exit(app.exec_())