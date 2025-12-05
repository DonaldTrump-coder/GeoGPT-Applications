import time
import os
from DroneController import DroneController
from Agent_Processor import Agent_Processor
from PyQt5 import QtWidgets,QtCore
import sys
from ui.dronetask_display import Drone_Window
from utils.text_tools import extract_last_json_dict
import json

stream_url="http://127.0.0.1"#推流的地址（测试用的本机）
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-gpu-rasterization --ignore-gpu-blacklist --enable-zero-copy'
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseOpenGLES)
#利用GPU，进行推流渲染的加速

#创建一个新线程，用来执行无人机任务（和UI分开）
class DroneTaskThread(QtCore.QThread):
    #信号槽，用来进行无人机控制端和前端数据交互
    log_signal = QtCore.pyqtSignal(str)
    captured_signal=QtCore.pyqtSignal(str)#拍摄照片后执行的信号
    assist_signal=QtCore.pyqtSignal(str)#获取修改后的描述文本信号
    send_description_signal=QtCore.pyqtSignal(str)#向界面发送描述文本

    #规定传输消息的格式：["发送者","消息内容"]
    message_signal=QtCore.pyqtSignal(list)#传输消息后执行的信号

    def __init__(self, drone:DroneController, analyzer:Agent_Processor, parent=None):
        super().__init__(parent)
        self.drone=drone
        self.analyzer=analyzer
        self.assist=False
        self.loop=None
        self.assist_result=None#修改过后的描述（界面输出的）

    def run(self):
        # 任务执行
        self.analyzer.input_task_positions(starting_x=self.drone.starting_UE_position_x,
                                           starting_y=self.drone.starting_UE_position_y,
                                           starting_z=self.drone.starting_UE_position_z,
                                           object_x=self.drone.object_UE_position_x,
                                           object_y=self.drone.object_UE_position_y,
                                           object_z=self.drone.object_UE_position_z
                                           )
        if self.assist is True:
            self.message_signal.emit(['GeoGPT','任务开始，无人机起飞'])
        else:
            self.message_signal.emit(['VLM','任务开始，无人机起飞'])
        self.drone.takeoff(altitude=15)
        self.drone.get_drone_state()
        self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)

        if self.assist is True:
            self.analyzer.add_messages('user',self.analyzer.GeoGPT_prompts+self.analyzer.control_prompts+self.analyzer.state_prompts)
            self.analyzer.add_messages('assistant','{ "take off": 15 }')
        else:
            self.analyzer.add_vlm_messages('user', None, self.analyzer.VLM_prompts+self.analyzer.vlm_control_prompts+self.analyzer.state_prompts)
            self.analyzer.add_vlm_messages('assistant', None, '{ "take off": 15 }')
        self.stop=False

        while(self.stop is False):
            if self.assist is True:
                self.actions=self.analyzer.post_large_language_model() # 调用模型
            else:
                self.actions=self.analyzer.post_vlm()
            self.action=extract_last_json_dict(self.actions) # 从模型输出中解析出动作
            if self.assist is True:
                self.analyze_action(self.action)
            else:
                self.analyze_vlm_action(self.action)

        if self.assist is True:
            self.message_signal.emit(['GeoGPT','任务完成，无人机降落'])
        else:
            self.message_signal.emit(['VLM','任务完成，无人机降落'])
        self.drone.land()

    def handle_assist(self,text):
        self.assist_result=text
        if self.loop is not None:
            self.loop.quit()

    # 解析视觉语言模型的动作输出结果并存入消息记录
    def analyze_vlm_action(self, action:dict):
        self.analyzer.delete_message()
        if action is None:#默认拍摄前方照片
            img_path=self.drone.capture_images("captures",f"{self.drone.capture_times}")
            self.drone.capture_times+=1
            self.captured_signal.emit(img_path)
            img_name=img_path+"_front.png"
            self.message_signal.emit(['VLM',f"Get front image"])
            action = {'get image': 'front'}
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', img_name, "Here is the front image." + self.analyzer.state_prompts + "Please output next action.")
        elif list(action.keys())[0]=='turn left':
            self.drone.turn_left(float(action['turn left']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Turn left {action['turn left']}°"])
        elif list(action.keys())[0]=='turn right':
            self.drone.turn_right(float(action['turn right']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Turn right {action['turn right']}°"])
        elif list(action.keys())[0]=='move forward':
            self.drone.move_forward(float(action['move forward']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Move forward {action['move forward']}m"])
        elif list(action.keys())[0]=='move backward':
            self.drone.move_backward(float(action['move backward']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Move backward {action['move backward']}m"])
        elif list(action.keys())[0]=='move up':
            self.drone.move_up(float(action['move up']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Move up {action['move up']}m"])
        elif list(action.keys())[0]=='move down':
            self.drone.move_up(float(action['move down']))
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', None, self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['VLM',f"Move down {action['move down']}m"])
        elif list(action.keys())[0]=='get image':
            img_path=self.drone.capture_images("captures",f"{self.drone.capture_times}")
            self.drone.capture_times+=1
            self.captured_signal.emit(img_path)
            img_name=img_path+"_"+action["get image"]+".png"
            self.analyzer.add_vlm_messages('assistant', None, json.dumps(action))
            self.message_signal.emit(['VLM',f"Get {action['get image']} image"])
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_vlm_messages('user', img_name, "Here is the "+ action["get image"] + " image." + self.analyzer.state_prompts + "Please output next action.")
        elif list(action.keys())[0]=='land':
            self.stop=True
            self.message_signal.emit(['VLM',"Land"])

    #解析模型输出，并直接执行模型指令
    def analyze_action(self, action:dict):
        self.analyzer.delete_message()
        if action is None:#默认拍摄前方照片
            img_path=self.drone.capture_images("captures",f"{self.drone.capture_times}")
            self.drone.capture_times+=1
            self.captured_signal.emit(img_path)
            img_name=img_path+"_front.png"
            self.analyzer.descriptions=self.analyzer.get_descriptions(img_name)
            self.message_signal.emit(['GeoGPT',f"Get front image"])
            if self.assist is True:
                self.send_description_signal.emit(self.analyzer.descriptions)
                self.loop=QtCore.QEventLoop()
                self.loop.exec_()
                self.analyzer.descriptions=self.assist_result
                self.message_signal.emit(['user',"The front image description is: "+self.analyzer.descriptions])
                self.analyzer.add_messages('assistant',json.dumps(action))
                self.drone.get_drone_state()
                self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
                self.analyzer.add_messages('user',"The front image description is: "+self.analyzer.descriptions+self.analyzer.state_prompts+"Please output next action.")
            else:
                self.message_signal.emit(['VLM',"The front image description is: "+self.analyzer.descriptions])
                self.analyzer.add_messages('assistant',json.dumps(action))
                self.drone.get_drone_state()
                self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
                self.analyzer.add_messages('user',"The front image description is: "+self.analyzer.descriptions+self.analyzer.state_prompts+"Please output next action.")
        elif list(action.keys())[0]=='turn left':
            self.drone.turn_left(float(action['turn left']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Turn left {action['turn left']}°"])
        elif list(action.keys())[0]=='turn right':
            self.drone.turn_right(float(action['turn right']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Turn right {action['turn right']}°"])
        elif list(action.keys())[0]=='move forward':
            self.drone.move_forward(float(action['move forward']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Move forward {action['move forward']}m"])
        elif list(action.keys())[0]=='move backward':
            self.drone.move_backward(float(action['move backward']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Move backward {action['move backward']}m"])
        elif list(action.keys())[0]=='move up':
            self.drone.move_up(float(action['move up']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Move up {action['move up']}m"])
        elif list(action.keys())[0]=='move down':
            self.drone.move_up(float(action['move down']))
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.drone.get_drone_state()
            self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
            self.analyzer.add_messages('user',self.analyzer.state_prompts+"Please output next action.")
            self.message_signal.emit(['GeoGPT',f"Move down {action['move down']}m"])
        elif list(action.keys())[0]=='get image':
            img_path=self.drone.capture_images("captures",f"{self.drone.capture_times}")
            self.drone.capture_times+=1
            self.captured_signal.emit(img_path)
            img_name=img_path+"_"+action["get image"]+".png"
            self.analyzer.descriptions=self.analyzer.get_descriptions(img_name)
            self.analyzer.add_messages('assistant',json.dumps(action))
            self.message_signal.emit(['GeoGPT',f"Get {action['get image']} image"])
            if self.assist is True:
                self.send_description_signal.emit(self.analyzer.descriptions)
                self.loop=QtCore.QEventLoop()
                self.loop.exec_()
                self.analyzer.descriptions=self.assist_result
                self.message_signal.emit(['user',"The"+action["get image"]+"image description is: "+self.analyzer.descriptions])
                self.drone.get_drone_state()
                self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
                self.analyzer.add_messages('user',"The "+action["get image"]+" image description is: "+self.analyzer.descriptions+self.analyzer.state_prompts+"Please output next action.")
            else:
                self.message_signal.emit(['VLM',"The"+action["get image"]+"image description is: "+self.analyzer.descriptions])
                self.drone.get_drone_state()
                self.analyzer.get_drone_state_prompts(self.drone.x,self.drone.y,self.drone.z)
                self.analyzer.add_messages('user',"The "+action["get image"]+" image description is: "+self.analyzer.descriptions+self.analyzer.state_prompts+"Please output next action.")
        elif list(action.keys())[0]=='land':
            self.stop=True
            self.message_signal.emit(['GeoGPT',"Land"])

    def assist_change(self,checked:bool):
        if checked:
            self.assist=True
        else:
            self.assist=False

# 主任务流程
def main():
    # 初始化
    drone = DroneController()
    # 配置硅基流动平台和GeoGPT的参数
    analyzer = Agent_Processor(
        api_key_silicon="sk-qgspupbsugmoknadoxohwuquyjfgtaljqspethzzywthvhgx",#硅基流动的API密钥
        siliconflow_url="https://api.siliconflow.cn/v1",#硅基流动的域名
        siliconflow_model="Pro/Qwen/Qwen2.5-VL-7B-Instruct",#视觉语言模型
        api_key_geogpt="access_token",#GeoGPT的API密钥
        geogpt_url="https://geogpt.zero2x.org.cn/",#GeoGPT的域名
        connect_url="be-api/service/api/geoChat/generate",#GeoGPT连接模型获取sessionId的地址
        message_url="be-api/service/api/geoChat/sendMsg",#GeoGPT向模型发送消息的地址
        large_models_url="be-api/service/api/model/v1/chat/completions",#GeoGPT大模型的开源地址
        geogpt_module="Qwen2.5-72B-GeoGPT"#GeoGPT发送消息的模型
    )

    # 创建保存目录
    os.makedirs("captures", exist_ok=True)#无人机拍摄的相片保存在该文件夹下

    app=QtWidgets.QApplication(sys.argv)
    window=Drone_Window(url=stream_url)#创建窗口
    window.show()

    #定义独立线程的UE无人机任务，和界面分开
    drone_task_thread=DroneTaskThread(drone,analyzer)

    #定义无人机任务和界面交互的信号
    drone_task_thread.captured_signal.connect(window.show_captured_image)
    drone_task_thread.message_signal.connect(window.send_message)
    drone_task_thread.send_description_signal.connect(window.send_descriptions)
    window.content.video_and_images.switch.toggled.connect(drone_task_thread.assist_change)
    drone_task_thread.assist_signal.connect(drone_task_thread.handle_assist)

    window.get_assist_signal(drone_task_thread.assist_signal)
    #将获取修改后的描述文本信号送至界面

    #开启UE线程
    drone_task_thread.start()

    sys.exit(app.exec_())

#运行main函数
if __name__ == "__main__":
    main()