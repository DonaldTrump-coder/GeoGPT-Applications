import time
import os
from DroneController import DroneController
from Agent_Processor import Agent_Processor
from PyQt5 import QtWidgets,QtCore
import sys
from ui.dronetask_display import Drone_Window
from utils.text_tools import extract_last_json_dict

stream_url="http://127.0.0.1"
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-gpu-rasterization --ignore-gpu-blacklist --enable-zero-copy'
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseOpenGLES)
#利用GPU，进行推流渲染的加速

#创建一个新线程，用来执行无人机任务（和UI分开）
class DroneTaskThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    finished_signal = QtCore.pyqtSignal()
    captured_signal=QtCore.pyqtSignal(str)#拍摄照片后执行的信号

    #规定传输消息的格式：["发送者","消息内容"]
    message_signal=QtCore.pyqtSignal(list)#传输消息后执行的信号

    def __init__(self, drone:DroneController, analyzer:Agent_Processor,parent=None):
        super().__init__(parent)
        self.drone=drone
        self.analyzer=analyzer

    def run(self):
        # 任务执行
        print("【任务开始】无人机起飞...")
        self.log_signal.emit("【任务开始】无人机起飞...")
        self.drone.takeoff(altitude=15)
        self.drone.get_drone_state()
        self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)

        self.analyzer.add_messages('assistant','{ "take off":"15" }')

        self.analyzer.add_messages('user',self.analyzer.GeoGPT_prompts+self.analyzer.control_prompts+self.analyzer.state_prompts)
        self.stop=False

        #while(self.stop is False):
        self.actions=self.analyzer.post_large_language_model()
        print(self.actions)
        self.actions=extract_last_json_dict(self.actions)
        print(self.actions)

        self.message_signal.emit(['VLM','received'])
        time.sleep(5)
        self.message_signal.emit(['VLM','你好'])

        print("\n【任务完成】无人机降落...")
        self.log_signal.emit("\n【任务完成】无人机降落...")
        self.drone.land()

    #解析模型输出，并直接执行模型指令
    def analyze_action(self, action:dict):
        if list(action.keys())[0]=='turn left':
            self.drone.turn_left(action['turn left'])
            self.analyzer.descriptions=""
        elif list(action.keys())[0]=='turn right':
            self.drone.turn_right(action['turn right'])
            self.analyzer.descriptions=""
        elif list(action.keys())[0]=='move forward':
            self.drone.move_forward(action['move forward'])
            self.analyzer.descriptions=""
        elif list(action.keys())[0]=='move backward':
            self.drone.move_backward(action['move backward'])
            self.analyzer.descriptions=""
        elif list(action.keys())[0]=='get image':
            img_path=self.drone.capture_images("captures",self.drone.capture_times)
            self.drone.capture_times+=1
            self.captured_signal.emit(img_path)
            img_name=img_path+"_"+action["get image"]+".png"
            self.analyzer.descriptions=self.analyzer.get_descriptions(img_name)
        elif list(action.keys())[0]=='land':
            self.stop=True

# 主任务流程
def main():
    # 初始化
    drone = DroneController()
    # 配置硅基流动平台和GeoGPT的参数
    analyzer = Agent_Processor(
        api_key_silicon="sk-ucdvpplmrrmguxcdciuxpdwftmrnstysomigzkjpgwlbkwsx",
        siliconflow_url="https://api.siliconflow.cn/v1",
        siliconflow_model="THUDM/GLM-4.1V-9B-Thinking",
        api_key_geogpt="sk-E9ZjEK01SiYTG78KDDUF",
        geogpt_url="https://geogpt.zero2x.org.cn/",
        connect_url="be-api/service/api/geoChat/generate",
        message_url="be-api/service/api/geoChat/sendMsg",
        large_models_url="be-api/service/api/model/v1/chat/completions",
        geogpt_module="Qwen2.5-72B-GeoGPT"
    )

    # 创建保存目录
    os.makedirs("captures", exist_ok=True)

    app=QtWidgets.QApplication(sys.argv)
    window=Drone_Window(url=stream_url)
    window.show()

    drone_task_thread=DroneTaskThread(drone,analyzer)
    drone_task_thread.captured_signal.connect(window.show_captured_image)
    drone_task_thread.message_signal.connect(window.send_message)

    drone_task_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()