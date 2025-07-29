from openai import OpenAI
from utils.image_tools import image2base64
import requests
import json

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
                large_models_url: str,# geogpt大模型发送消息的地址
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
        self.api_url=geogpt_url+large_models_url
        self.geogpt_model=geogpt_module

        self.messages=[]
        self.init_prompts()

    def init_prompts(self):
        #用视觉语言模型描述图像的提示词
        self.description_prompts="You are helping a drone decide how to conduct its action. The image can be from one of the front, down, back, left, or right view directions of the drone cameras. Now please describe the image about what the image is, the necessary elements and their relative positional relations, in order to help others fully understand the image without seeing the image."

        self.descriptions=""

        #用GeoGPT进行决策的提示词
        self.GeoGPT_prompts="Now you are controlling a drone to finish a task of sending medical tools or medicine to a patient object. You need to control the drone to take off, cruising from the starting point to near the object, and land correctly beside the object place. You will be provided with the description of the elements of the image, the status information of the drone and the actions you can take. You need to choose to take actions to finish evey step during the task."

        #定义模型能够输出的指令
        self.control_prompts="The actions must be outputed in the dict format: { action: parameter }. Here are the actions that can be outputed: 1.'turn left': turn around the drone to its left side with the parameter as degree; 2.'turn right': turn around the drone to its right side with the parameter as degree; 3.'move forward': move the drone to its front side with the parameter as meter; 4.'move backward': move the drone to its back side with the parameter as meter; 5.'move up': move the drone to a higher place with the parameter as meter; 6.'move down': move the drone to a lower place with the parameter as meter; 7.'get image': obtain the next image taken from the drone, which has five camera directions, and the parameter must be one of the ['front', 'down', 'back', 'left', 'right'] (The image is in the form of natural language description, and you must understand it). 8.'take off': start the task and control the drone to take off to a certain height with the parameter as meter. 9.'land': when the drone arrives at the right place, land to finish the task, with the parameter as meters per second(landing speed). Usually, 'get image' must be taken after every other action, on order to control the drone accurately. If you can not see the task object or decide what to do, you should also get another image again. Only output an action dict at a time, for example { 'get image': 'front' }."

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

    #添加AI模块中的角色和消息信息
    def add_messages(self,role,content):
        self.messages.append({
            "role": role,
            "content": content
        })

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

    #调用geogpt大语言模型，获取指令
    #调用模型之前将相关提示词加到self.messages中
    def post_large_language_model(self)->str:
        headers = {
        "authorization": f"Bearer {self.api_key_geogpt}",
        "Content-Type": "application/json"
        }
        payload={
            "messages":self.messages,
            "stream":True
        }
        responses = []  # Store all response chunks

        # Send POST request (enable streaming response)
        with requests.post(self.api_url, headers=headers, json=payload, stream=True) as response:
            # Check response status
            response.raise_for_status()

            for chunk in response.iter_lines():
                # Filter out keep-alive new lines
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    # Handle possible Server-Sent Events (SSE) format
                    if decoded_chunk.startswith("data:"):
                        json_str = decoded_chunk[5:]
                    else:
                        json_str = decoded_chunk

                    # Check for message event tag
                    if json_str == 'event:message':
                        continue
                    # Check for end flag
                    if json_str.strip() == "[DONE]":
                        break
                            
                    # Unescape handling:
                    # 1. Replace \" with "
                    # 2. Replace \\ with \
                    unescaped_str = json_str.replace('\\"', '"').replace('\\\\', '\\')

                    if unescaped_str.startswith('"') and unescaped_str.endswith('"'):
                        # Remove outer quotes
                        unescaped_str = unescaped_str[1:-1]

                        # Parse JSON
                    #data = json.loads(unescaped_str)
                    data=json.loads(json_str)
                    responses.append(data)  # Save response
        full_content=""
        for response in responses:
            if 'choices' in response and response['choices']:
                content = response['choices'][0]['delta']['content']
                full_content += content
        return full_content

    def get_drone_state_prompts(self,x,y,z):
        self.state_prompts=f"The current position state information: The x-position of the drone is {x}. The y-position is {y}. The z-position is {z}."
