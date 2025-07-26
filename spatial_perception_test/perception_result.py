from utils.image_overlap import BboxIouCalculator
import os
from PIL import Image
from tqdm import tqdm

image_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\images"
question_floder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\question"
perception_folder="C:\\Users\\10527\\Desktop\\GeoGPT\\data\\Aerial_Visual_Grounding\\perception"

if __name__=="__main__":
    rate_sum=0
    times=0
    for perception in tqdm(os.listdir(perception_folder),desc="计算重合度..."):
    #for perception in os.listdir(perception_folder):
        question=perception[:-4]+".json"
        for image in os.listdir(image_folder):
            if image[:-4]+"_" in perception[:-4] or image[:-4]==perception[:-4]:
                w,h=Image.open(image_folder+"\\"+image).size
                calculator=BboxIouCalculator(question_floder+"\\"+question,
                                             perception_folder+"\\"+perception,
                                             h,
                                             w
                                             )
                rate_sum+=calculator.calculate_iou()
                times+=1
                break
    print("计算完成")
    print(rate_sum/times)