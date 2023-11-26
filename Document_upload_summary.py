'''
星火文档
https://www.xfyun.cn/doc/spark/ChatDoc-API.html#%E4%B8%80%E3%80%81%E6%9C%8D%E5%8A%A1%E4%BB%8B%E7%BB%8D


'''
# -*- coding:utf-8 -*-
import hashlib
import base64
import hmac
import time
import random
from urllib.parse import urlencode
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
# pip install requests_toolbelt -i https://pypi.tuna.tsinghua.edu.cn/simple



class Document_Upload_Summary:
    def __init__(self, APPId, APISecret):
        self.APPId = APPId
        self.APISecret = APISecret
        #self.Timestamp = timestamp
        self.upload_request_url = "https://chatdoc.xfyun.cn/openapi/fileUpload"
        self.summary_request_url = 'https://chatdoc.xfyun.cn/openapi/startSummary'
        
    def get_origin_signature(self):
        self.Timestamp = str(int(time.time()))
        m2 = hashlib.md5()
        data = bytes(self.APPId + self.Timestamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum


    def get_signature(self):
        # 获取原始签名
        signature_origin = self.get_origin_signature()
        # 使用加密键加密文本
        signature = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha1).digest()
        # base64密文编码
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        return signature

    def get_header(self):
        signature = self.get_signature()
        header = {
            "appId": self.APPId,
            "timestamp": self.Timestamp,
            "signature": signature,
        }
        return header

    # 提交本地文件
    def upload_files(self,files,body):
        #files, body = document_upload.get_files_and_body()
        headers = self.get_header()
        response = requests.post(self.upload_request_url, files=files, data=body, headers=headers)
        return response

    # 文档总结
    def file_summary(self,fileid):
        headers = self.get_header()
        
        response = requests.post(self.summary_request_url,\
                                 data={'fileId':fileid},\
                                     #fileId = '43816997a7a44a299d0bfb7c360c5838',
                                     headers=headers)
        return response

if __name__ == '__main__':
    APPId = "xxxx"
    APISecret = "xxxx"
    
    dus = Document_Upload_Summary(APPId, APISecret)
    
    # 本地文档上传
    files = {'file': open('背影.txt', 'rb')}
    body = {
                "url": "",
                "fileName": "背影.txt",
                "fileType": "wiki",     # 固定值
                "needSummary": False,
                "stepByStep": False,
                "callbackUrl": "your_callbackUrl",
            }
    
    response = dus.upload_files(files,body)
    if response.json()['code'] == 0:
        print(f'请求的文件FIleId:{response.json()["data"]["fileId"]}')
    
    
    # 文档总结
    fileid = 'xxxx'
    response = dus.file_summary(fileid)
    response.json()
    
    