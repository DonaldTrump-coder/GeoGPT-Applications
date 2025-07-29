import re
import json

def extract_last_json_dict(text):
    # 提取所有 {...} 模式的 JSON 字典
    matches = re.findall(r"\{.*?\}", text, re.DOTALL)
    for json_str in reversed(matches):  # 从最后一个开始尝试解析
        try:
            clean_str = json_str.replace("'", '"')
            return json.loads(clean_str)
        except json.JSONDecodeError:
            continue  # 尝试前一个
    return None