from dronetask_display import Drone_Window
import sys
from PyQt5 import QtWidgets,QtCore

app=QtWidgets.QApplication(sys.argv)
window=Drone_Window()
window.show()
sys.exit(app.exec_())