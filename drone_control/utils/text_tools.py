import re
import json

def extract_dict_block(text:str):
    # 找到形如 { ... } 的 JSON 字典
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        json_str = match.group()
        # 替换单引号为双引号
        json_str = json_str.replace("'", '"')
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("JSON decode failed:", e)
            print("json_str:", json_str)
            return None
    return None