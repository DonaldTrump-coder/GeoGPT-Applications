import time
import os
from DroneController import DroneController
from Agent_Processor import Agent_Processor
from PyQt5 import QtWidgets,QtCore
import sys
from ui.dronetask_display import Drone_Window

#创建一个新线程，用来执行无人机任务（和UI分开）
class DroneTaskThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, drone, analyzer,parent=None):
        super().__init__(parent)
        self.drone=drone
        self.analyzer=analyzer

    def run(self):
        try:
        # 任务执行
            print("【任务开始】无人机起飞...")
            self.log_signal.emit("【任务开始】无人机起飞...")
            self.drone.takeoff(altitude=15)

            for i in range(3):  # 拍摄3张不同角度照片
                print(f"\n【拍摄第{i + 1}张照片】")
                self.log_signal.emit(f"\n【拍摄第{i + 1}张照片】")
                img_path = f"captures/scene_{i}.png"
                self.drone.capture_image(img_path)

                # 分析场景内容（问题适配模型的理解范围）
                question = "请详细描述当前场景中可见的主要物体、它们的颜色和空间分布关系"
                print(f"\n【场景分析结果】")
                analysis = self.analyzer.analyze_scene(img_path, question)
                print(analysis)

                time.sleep(3)  # 增加间隔时间，避免请求过于频繁
                self.drone.turn_left(3.14/2).join()

            self.drone.go_back()

        except Exception as e:
            print(f"\n【任务执行错误】{str(e)}")
            self.log_signal.emit(f"\n【任务执行错误】{str(e)}")
        finally:
            print("\n【任务完成】无人机降落...")
            self.log_signal.emit("\n【任务完成】无人机降落...")
            self.drone.land()

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
        geogpt_module="Qwen2.5-72B-GeoGPT"
    )

    # 创建保存目录
    os.makedirs("captures", exist_ok=True)

    app=QtWidgets.QApplication(sys.argv)
    window=Drone_Window()
    window.show()

    drone_task_thread=DroneTaskThread(drone,analyzer)

    drone_task_thread.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()