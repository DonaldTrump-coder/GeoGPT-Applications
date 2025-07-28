from openai import OpenAI
from utils.image_tools import image2base64

# 初始化大模型API（适配硅基流动平台和GeoGPT）
class Agent_Processor:
    def __init__(self,
                api_key_silicon: str,# 硅基流动的api key
                siliconflow_url: str,# 硅基流动的总域名
                siliconflow_model: str,# 硅基流动调用的模型
                api_key_geogpt: str,# geogpt的api key
                geogpt_url: str,# geogpt的总域名
                connect_url: str,# geogpt建立连接的地址
                message_url: str,# geogpt发送消息的地址
                geogpt_module: str# geogpt的模型
                ):
        self.silicon_client = OpenAI(
            api_key=api_key_silicon,
            base_url=siliconflow_url
        )
        self.silicon_model=siliconflow_model
        self.api_key_geogpt=api_key_geogpt
        self.connect_url=geogpt_url+connect_url
        self.message_url=geogpt_url+message_url
        self.geogpt_model=geogpt_module

    def init_prompts(self):
        #用视觉语言模型描述图像的提示词
        self.description_prompts="You are helping a drone decide how to conduct its action. The image can be from one of the front, down, back, left, or right view directions of the drone cameras. Now please describe the image about what the image is, the necessary elements and their relative positional relations, in order to help others fully understand the image without seeing the image."

        #用GeoGPT进行决策的提示词
        self.GeoGPT_prompts="Now you are controlling a drone to finish a task of sending medical tools or medicine to a patient object. You need to control the drone to take off, cruising from the starting point to near the object, and land correctly beside the object place. You will be provided with the description of the elements of the image and the actions you can take. You need to choose to take actions to finish evey step during the task."

        #定义模型能够输出的指令
        self.controlprompts="The actions must be outputed in the dict format: {action: parameter}. Here are the actions that can be outputed: 1.turn left:"

    #调用硅基流动的视觉语言模型进行图像描述，返回图像描述的文本
    def get_descriptions(self,image_path:str)->str:
        encoded_image=image2base64(image_path=image_path)
        try:
            response = self.silicon_client.chat.completions.create(
                model=self.silicon_model,  # 硅基流动平台的视觉模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", 
                             "text": self.description_prompts},
                            {"type": "image_url", 
                             "image_url": {
                                "url": encoded_image,
                                "detail":"auto"
                            }}
                        ]
                    }
                ],
                stream=True
            )

            full_content = ""
            for chunk in response:
                if not chunk.choices:
                    continue
                if chunk.choices[0].delta.content:#模型新增的输出内容
                    full_content+=chunk.choices[0].delta.content
                #if chunk.choices[0].delta.reasoning_content:#模型推理部分的内容（不需要的话可直接注释掉此部分）
                #print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
            return full_content

        except Exception as e:
            print(f"\n【读图错误】{str(e)}")
            return "Description failed"

    #给定图像路径和问题，输出对图像的分析
    def analyze_scene(self, image_path: str, question: str) -> str:
        """分析场景图片并回答问题（适配GLM-4.1V模型格式）"""
        # 读取图像并转换为base64编码（硅基流动平台要求的图像格式）
        encoded_image=image2base64(image_path=image_path)

        try:
            response = self.silicon_client.chat.completions.create(
                model=self.silicon_model,  # 硅基流动平台的视觉模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {
                                "url": encoded_image,"detail":"auto"
                            }}
                        ]
                    }
                ],
                stream=True
            )

            full_content = ""
            for chunk in response:
                if not chunk.choices:
                    continue
                if chunk.choices[0].delta.content:#模型新增的输出内容
                    full_content+=chunk.choices[0].delta.content
                #if chunk.choices[0].delta.reasoning_content:#模型推理部分的内容（不需要的话可直接注释掉此部分）
                #print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
            return full_content

        except Exception as e:
            print(f"\n【分析错误】{str(e)}")
            return None