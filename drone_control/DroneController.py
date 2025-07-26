import airsim
import cv2
import numpy as np

class DroneController:
    def __init__(self):# 初始化AirSim无人机控制
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

    def takeoff(self, altitude: float = 10):
        """起飞到指定高度（米）"""
        self.client.takeoffAsync().join()
        self.client.moveToZAsync(-altitude, 5).join()

    def capture_image(self, save_path: str) -> str:
        """拍摄场景照片并保存"""

        response = self.client.simGetImage(
            "0", image_type=airsim.ImageType.Scene
        )
        frame = cv2.imdecode(np.frombuffer(response, np.uint8), cv2.IMREAD_COLOR)
        cv2.imwrite(save_path,frame)
        #airsim.write_file(save_path, responses[0].image_data_uint8)
        return save_path
    
    def go_back(self):
        self.client.goHomeAsync().join()
        print("无人机已返回")

    def turn_left(self,rad):
        return self.client.moveByRollPitchYawThrottleAsync(0,0,rad,0.5,3)

    def land(self):
        """安全降落"""
        self.client.landAsync().join()
        self.client.armDisarm(False)