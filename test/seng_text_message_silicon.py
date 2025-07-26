from openai import OpenAI

api_key="sk-ucdvpplmrrmguxcdciuxpdwftmrnstysomigzkjpgwlbkwsx"#API密钥（硅基流动上注册）
base_url="https://api.siliconflow.cn/v1"#硅基流动域名
model="THUDM/GLM-4.1V-9B-Thinking"#硅基流动中的模型

def send_messages(model):
    client=OpenAI(api_key=api_key,base_url=base_url)

    #获取流式响应
    response=client.chat.completions.create(model=model,
                                            messages=[
                                                {'role':'user',#消息列表中使用者提出的问题
                                                'content':'你是谁？'#具体问题
                                                }
                                            ],
                                            stream=True)
    
    #解析每一段流式响应
    for chunk in response:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content:#模型新增的输出内容
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.choices[0].delta.reasoning_content:#模型推理部分的内容（不需要的话可直接注释掉此部分）
            print(chunk.choices[0].delta.reasoning_content, end="", flush=True)

if __name__=="__main__":
    send_messages(model=model)