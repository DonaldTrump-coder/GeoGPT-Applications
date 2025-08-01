import requests
import warnings
from typing import Callable
import re
import urllib.parse
import json

domain="https://geogpt.zero2x.org.cn" #GeoGPT的总域名
url="/be-api/service/api/geoChat/sendMsg" #发送信息进行对话的网址
access_token="access_token" #API-key
question="这张图片里有什么？" #进行对话的问题
sessionId="882cd3e0-d19a-41cf-a285-5cfae7ea506f" #对话的ID（需要从连接模型的数据中获取）
module="GeoGPT-R1-Preview" #选择模型

#分段处理模型传来的流式数据
def handle_text_stream(url:str,#访问模型的地址
                       access_token:str,
                       payload:dict,#发给模型的数据
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
        err_msg=f"Streaming connection error: {str(e)}"
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
        content_decoded=parsed[0]["content"]["content"]
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

if __name__=="__main__":
    try:
        handle_text_stream(url=domain+url,
                           access_token=access_token,
                           payload={
                            "text":question,
                            "sessionId":sessionId,
                            "module":module
                           },
                           callback=demo
                           )
    except KeyboardInterrupt:
        print("\nUser initiated connection termination")