import json
from typing import Union, List
import logging
import math

#文件路径
path_json = "C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\question\\visual_grounding_0_1.json"
path_txt = "C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\perception\\test.txt"

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#使用方法：直接传入json文件和txt文件的路径，就可以做一次计算了
class BboxIouCalculator:
#计算器
    def __init__(self,
                 bbox1: Union[List[int], str] = None,#列表&&文件路径
                 bbox2: Union[List[int], str] = None,#列表&&文件路径
                 height=0,
                 width=0
                 ):
        self.bbox1 = bbox1
        self.bbox2 = bbox2
        self.bbox1_key = 'Answer'
        self.bbox1_file_type = 'json'.lower()
        self.bbox2_file_type = 'txt'.lower()
        self.h=height
        self.w=width

#加载矩形框数据
    def _load_bbox_from_file(self,
                             file_path: str,#文件路径
                             file_type: str,#文件类型
                             key: str = None) -> List[int]:#键
#return: 矩形框坐标列表[xmin, ymin, xmax, ymax]
        try:
            if file_type == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if key is None:
                    key = self.bbox1_key
                return data[key]
            elif file_type == 'txt':
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    # 处理txt文件中的格式，如"[414, 252, 441, 353]"
                    if content.startswith('[') and content.endswith(']'):
                        return [int(x.strip()) for x in content[1:-1].split(',')]
                    else:
                        raise ValueError("TXT文件格式不正确，应为[xmin, ymin, xmax, ymax]")
            else:
                raise ValueError(f"不支持的文件类型: {file_type}")
        except Exception as e:
            raise ValueError(f"加载文件失败: {str(e)}")

    def _validate_bbox(self, bbox: List[int]) -> None:
#验证矩形框格式是否正确
        if len(bbox) != 4:
            print(self.bbox1)
            raise ValueError("矩形框必须有4个值[xmin, ymin, xmax, ymax]")
        if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            print(self.bbox1)
            raise ValueError("矩形框坐标无效: xmin应小于xmax, ymin应小于ymax")

#获取矩形框数据
    def get_bbox(self,
                 bbox: Union[List[int], str],#数据&&文件路径
                 file_type: str = None,#文件类型
                 key: str = None) -> List[int]:#键
#return: 矩形框坐标列表[xmin, ymin, xmax, ymax]
        if isinstance(bbox, str):
            if file_type is None:
                if hasattr(self, 'bbox1_file_type'):
                    file_type = self.bbox1_file_type
                else:
                    file_type = 'json'  # 默认值
            bbox_data = self._load_bbox_from_file(bbox, file_type, key)
        elif isinstance(bbox, (list, tuple)):
            bbox_data = list(bbox)
        else:
            raise ValueError("bbox参数必须是列表、元组或文件路径字符串")

        self._validate_bbox(bbox_data)
        return bbox_data
#计算交并比
    def calculate_iou(self, bbox1: Union[List[int], str, None] = None,
                      bbox2: Union[List[int], str, None] = None,
                      **kwargs) -> float:
#获取bbox1数据
        if bbox1 is None:
            if self.bbox1 is None:
                raise ValueError("未提供bbox1参数")
            bbox1_data = self.get_bbox(self.bbox1,
                                       kwargs.get('bbox1_file_type', self.bbox1_file_type),
                                       kwargs.get('bbox1_key', self.bbox1_key))
        else:
            bbox1_data = self.get_bbox(bbox1,
                                       kwargs.get('bbox1_file_type', None),
                                       kwargs.get('bbox1_key', None))

#获取bbox2数据
        if bbox2 is None:
            if self.bbox2 is None:
                raise ValueError("未提供bbox2参数")
            bbox2_data = self.get_bbox(self.bbox2,
                                       kwargs.get('bbox2_file_type', self.bbox2_file_type),
                                       kwargs.get('bbox2_key', None))
        else:
            bbox2_data = self.get_bbox(bbox2,
                                       kwargs.get('bbox2_file_type', None),
                                       kwargs.get('bbox2_key', None))

        w_rounded=int(math.floor(self.w/28)*28)
        h_rounded=int(math.floor(self.h/28)*28)
        pixels=w_rounded*h_rounded
        if pixels>=12544 and pixels<=1300012:
            new_w=w_rounded
            new_h=h_rounded
        else:
            scale=math.sqrt(1300012/pixels)
            new_w=int(w_rounded*scale)
            new_h=int(h_rounded*scale)
            new_w=int(math.floor(new_w/28)*28)
            new_h=int(math.floor(new_h/28)*28)
        bbox2_data[0]=(bbox2_data[0]*self.w)/new_w
        bbox2_data[2]=(bbox2_data[2]*self.w)/new_w
        bbox2_data[1]=(bbox2_data[1]*self.h)/new_h
        bbox2_data[3]=(bbox2_data[3]*self.h)/new_h

#计算交集区域坐标
        x_left = max(bbox1_data[0], bbox2_data[0])
        y_top = max(bbox1_data[1], bbox2_data[1])
        x_right = min(bbox1_data[2], bbox2_data[2])
        y_bottom = min(bbox1_data[3], bbox2_data[3])

#如果没有交集，返回0
        if x_right < x_left or y_bottom < y_top:
            return 0.0

#计算交集和并集面积
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        bbox1_area = (bbox1_data[2] - bbox1_data[0]) * (bbox1_data[3] - bbox1_data[1])#json文件中bounding box的面积
        #bbox2_area = (bbox2_data[2] - bbox2_data[0]) * (bbox2_data[3] - bbox2_data[1])#txt文件中bounding box的面积
        #union_area = bbox1_area + bbox2_area - intersection_area

#计算交并比
        iou = intersection_area / bbox1_area
        #iou = intersection_area / union_area
        return iou


if __name__ == "__main__":
    try:
        calculator = BboxIouCalculator(
            bbox1=path_json,
            bbox2=path_txt
        )
#计算交并比
        iou = calculator.calculate_iou()
        print(f"\n交并比: {iou:.4f}")
    except Exception as e:
        logger.error(f"计算过程中发生错误: {str(e)}")