import requests
import warnings
from typing import Callable
import re
import urllib.parse
import json
from image_description import get_file_list
import os

access_token="sk-E9ZjEK01SiYTG78KDDUF"
base_rul="https://geogpt.zero2x.org.cn/" #GeoGPT的总域名
connect_url="be-api/service/api/geoChat/generate"
message_url="be-api/service/api/geoChat/sendMsg"
module="Qwen2.5-72B-GeoGPT" #选择模型

#基础任务的提示词
basic_prompt="You receive a description of an image taken by a drone, with the descriptions of some main elements in the city and their corresponding bounding box, with the format of [xmin,ymin,xmax,ymax]. The language organization may be various, but is understandable. The task is to give a possible bounding box of the same format of[xmin,ymin,xmax,ymax] according to the object description. In this task, image description helps you to understand the image, and object description guides you to find the object bounding box. Please answer in the only format of [xmin,ymin,xmax,ymax]."

#创建连接，获取sessionId
def create_session(access_token,url):
    headers={
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response=requests.get(url,headers=headers,timeout=10)

        # Attempt to parse JSON response, fallback to text on failure
        try:
            response_data = response.json()
            print("连接成功...")
        except ValueError:
            response_data = response.text
                
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response_data
        }
    
    except requests.exceptions.RequestException as e:
        # Encapsulate error details
        error_info = {
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
        if isinstance(e, requests.exceptions.Timeout):
            error_info['timeout'] = 10
        raise requests.exceptions.RequestException(f"请求失败: {error_info}") from e
    
#分段处理模型传来的流式数据
def handle_text_stream(url:str,#访问模型的地址
                       access_token:str,
                       question:str,
                       sessionId:str,
                       module:str,#发给模型的数据
                       callback:Callable[[str],None],#处理每一段数据的回调函数（每次新接收到模型的数据就调用一次）
                       chunk_size:int=1024,
                       delimiter:str="\n\n"#分隔符
                       )->None:
    #请求头
    headers={
        'Authorization': f'Bearer {access_token}',
        'Accept': 'text/event-stream',
        'Content-Type': 'application/json'
    }

    buffer=''
    payload={
        "text":question,
        "sessionId":sessionId,
        "module":module
    }
    try:
        #向模型发送数据
        with requests.post(url,
                           headers=headers,
                           json=payload,
                           stream=True,
                           timeout=(3.05,30)
                           ) as resp:
            resp.raise_for_status()
            for byte_chunk in resp.iter_content(chunk_size=chunk_size):#读取每一段流式数据，处理每一段
                if not byte_chunk:
                    text_chunk=""
                else:
                    try:
                        text_chunk=byte_chunk.decode('utf-8')#对流式数据进行utf-8解码
                    except UnicodeDecodeError:
                        text_chunk=byte_chunk.decode('utf-8',errors='replace')
                        warnings.warn("Detected non-UTF-8 characters, replaced malformed bytes")

                buffer+=text_chunk#解码后的数据加入buffer区域
                while delimiter in buffer:#循环取出第一个分隔符前面的内容，进行打印等相关操作
                    event_raw,buffer=buffer.split(delimiter,1)
                    process_sse_event(event_raw.strip(), callback)
    except requests.exceptions.RequestException as e:
        error_msg=f"Streaming connection error: {str(e)}"
        if buffer:
            error_msg += f"\nUnprocessed buffer: {buffer[:200]}{'...' if len(buffer) > 200 else ''}"
        callback(f"[ERROR] {error_msg}")

#对单独取出的一段SSE事件进行处理
def process_sse_event(raw_event:str,
                      callback:Callable[[str],None])->None:
    event_lines=[line.strip() for line in raw_event.split('\n') if line.strip()]
    content_lines=[]
    for line in event_lines:
        #将data开头的内容作为数据
        if line.startswith('data:'):
            content=line[5:].lstrip()
            content_lines.append(content)
        elif line.startswith(':'):
            continue

    full_content='\n'.join(content_lines)#用换行符连接每一段内容
    if full_content:
        callback(full_content)

#对模型输出结果进行解码
def decode_from_xml(raw_text):
    match=re.search("<markdown>(.*?)</markdown>",raw_text)
    if not match:
        print("未找到内容")
        return None

    encoded=match.group(1)
    decoded_once=urllib.parse.unquote(encoded)

    try:
        parsed=json.loads(decoded_once)
        content_decoded=parsed[0]["content"]
    except Exception as e:
        print("Json解析失败:",e)
        return None

    final_content=urllib.parse.unquote(content_decoded)
    return final_content

last_result=""#不输出和上次相同的数据
def demo(content:str):
    global last_result
    if(content.startswith('[ERROR]')):
        print(f"\033[31m{content}\033[0m")
    else:
        if(decode_from_xml(content)==last_result):
            return None
        last_result=decode_from_xml(content)
        print(f"Received content: {decode_from_xml(content)}")

def read_json(filename):
    jsonfile=open(filename,'r',encoding='utf-8')
    return json.load(jsonfile)

def read_txt(filename):
    f=open(filename,'r',encoding='utf-8')
    return f.read()

def write_text(filename,text):
    f=open(filename,'w',encoding='utf-8')
    f.write(text)

#方便传参，函数嵌套定义
def save_file(filename):
    def callback(content:str):
        global last_result
        if(content.startswith('[ERROR]')):
            print(f"\033[31m{content}\033[0m")
        else:
            if(decode_from_xml(content)==last_result):
                return None
            last_result=decode_from_xml(content)
            write_text(filename,decode_from_xml(content))
    return callback
    
if __name__=="__main__":
    #先进行GeoGPT的连接
    sessionId=create_session(access_token=access_token,url=base_rul+connect_url)["data"]["data"]
    descriptions_floder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\descriptions"
    questions_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\question"
    perception_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\perception"
    questions=get_file_list(questions_folder)#question文件名
    image_descriptions=get_file_list(descriptions_floder)
    index=0
    for descrpition in image_descriptions:
        for question in questions:#对每一个question的json文本进行处理、提问
            if descrpition[:-4]+"_" in question or descrpition[:-4]==question[:-5]:
                index+=1
                if os.path.exists(perception_folder+"\\"+question[:-5]+".txt"):
                    continue
                #目标描述
                object_description=read_json(questions_folder+"\\"+question)["Question"]

                #图像描述
                image_description=read_txt(descriptions_floder+"\\"+descrpition)

                prompt=basic_prompt+"image description:"+image_description+"object description:"+object_description+"only return in format [xmin,ymin,xmax,ymax]"
                callback=save_file(perception_folder+"\\"+question[:-5]+".txt")
                print(f"正在感知第{index}张图像...")
                handle_text_stream(url=base_rul+message_url,
                                access_token=access_token,
                                question=prompt,
                                sessionId=sessionId,
                                module=module,
                                callback=callback
                                )
                print(f"完成第{index}张图像的感知...")