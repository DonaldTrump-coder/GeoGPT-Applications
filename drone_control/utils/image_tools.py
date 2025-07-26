import base64
import mimetypes

#图像转为base64格式
def image2base64(image_path:str)->str:
    mime_type,_=mimetypes.guess_type(image_path)
    image_file=open(image_path,'rb')
    encoded=base64.b64encode(image_file.read())
    return f"data:{mime_type};base64,"+encoded.decode('utf-8')