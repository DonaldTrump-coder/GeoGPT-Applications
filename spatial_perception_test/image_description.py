from openai import OpenAI
import base64
import os
import mimetypes

api_key="api_key"#API密钥（硅基流动上注册）
base_url="https://api.siliconflow.cn/v1"#硅基流动域名
model="THUDM/GLM-4.1V-9B-Thinking"#硅基流动中的模型

image_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\images"
object_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\descriptions\\"
text="The image is obtained from a drone.Please describe what the image has, in pixel levels, as detailed as possible. Describe as many elements as possible. Please describe the element and its bounding box in image pixels, with a format as [xmin,ymin,xmax,ymax]. xmin and ymin is the top-left of the bounding box, and xmax and ymax is the bottom-right of the bounding box. The description should both include the description and bounding box. For example, a white car heading towards the top of the image: [23,45,100,300]. Describe every element separately."

def send_messages(model,
                  text, #文本
                  image #image_url
                  ):
    client=OpenAI(api_key=api_key,base_url=base_url)

    #获取流式响应
    response=client.chat.completions.create(model=model,
                                            messages=[
                                                {
                                                'role':'user',#消息列表中使用者提出的问题
                                                'content':[{'type':'image_url','image_url':{'url':image,'detail':'auto'}},{'type':'text','text':text}]
                                                }
                                            ],
                                            stream=False)
    
    full_content=response.choices[0].message.content

    '''
    #解析每一段流式响应
    for chunk in response:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content:#模型新增的输出内容
            full_content+=chunk.choices[0].delta.content
        #if chunk.choices[0].delta.reasoning_content:#模型推理部分的内容（不需要的话可直接注释掉此部分）
            #print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
            '''

    return full_content

def write_content(text,filename):
    file=open(filename,'w',encoding='utf-8')
    file.write(text)

#图像转为base64格式
def image2base64(image_path:str)->str:
    mime_type,_=mimetypes.guess_type(image_path)
    image_file=open(image_path,'rb')
    encoded=base64.b64encode(image_file.read())
    return f"data:{mime_type};base64,"+encoded.decode('utf-8')

def get_file_list(folder_path):
    return os.listdir(folder_path)

if __name__=="__main__":
    folder_path=image_folder
    file_list=get_file_list(folder_path)
    index=1
    for file in file_list:
        if os.path.exists(object_folder+file[:-4]+".txt"):
            index+=1
            continue
        print(f"正在描述第{index}张图像...")
        content=send_messages(model,text=text,image=image2base64(folder_path+"\\"+file))
        write_content(content,object_folder+file[:-4]+".txt")
        print(f"第{index}张图像已描述完成")
        index+=1