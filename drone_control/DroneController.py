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
    
    def capture_images(self,save_dir,save_name: str)->str:
        #同时拍摄多张图像（）
        responses=self.client.simGetImages(
            [
                airsim.ImageRequest("front", airsim.ImageType.Scene, False, False),
                airsim.ImageRequest("down", airsim.ImageType.Scene, False, False),
                airsim.ImageRequest("back", airsim.ImageType.Scene, False, False),
                airsim.ImageRequest("left", airsim.ImageType.Scene, False, False),
                airsim.ImageRequest("right", airsim.ImageType.Scene, False, False)
            ]
        )
        image_names=[save_name+"_front.png",save_name+"_down.png",save_name+"_top.png",save_name+"_left.png",save_name+"_right.png"]
        save_dir=save_dir+"\\"
        for i, response in enumerate(responses):
            if response.width == 0:
                print(f"Failed to get image {image_names[i]}")
                continue

            frame = cv2.imdecode(np.frombuffer(response.image_data_uint8, np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite(save_dir+image_names[i], frame)
            print(f"Saved {image_names[i]}")
        
        return save_dir+save_name
    
    def go_back(self):
        self.client.goHomeAsync().join()
        print("无人机已返回")

    def turn_left(self,rad):
        return self.client.rotateByYawRateAsync(30, rad/30)

    def land(self):
        """安全降落"""
        self.client.landAsync().join()
        self.client.armDisarm(False)