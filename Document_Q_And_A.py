'''
文档url:
    https://www.xfyun.cn/doc/spark/ChatDoc-API.html#%E4%B8%89%E3%80%81%E6%8E%A5%E5%8F%A3%E5%88%97%E8%A1%A8

原理：
    - websocket是流式返回本篇通过Global recep_mesg进行对话截获，并返回
    单次跑有问题的话，会通过ON_Error报错

'''
# -*- coding:utf-8 -*-
import hashlib
import base64
import hmac
import time
from urllib.parse import urlencode
import json
import websocket
import _thread as thread
import ssl
recep_mesg = []

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("关闭代码：", close_status_code)
    print("关闭原因：", close_msg)

# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(ws.question)
    ws.send(data)

# 收到websocket消息的处理
def on_message(ws, message):
    #ws = self.ws
    global recep_mesg # 1
    print(message)
    data = json.loads(message)
    recep_mesg.append(data)
    code = data['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        content = data["content"]
        print('steamchat:',content)
        status = data["status"]
        # print(f'status = {status}')
        print(content, end='')
        if status == 2:
            ws.close()

class Document_Q_And_A:
    def __init__(self, APPId, APISecret,\
                wikiPromptTpl = "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",\
                wikiFilterScore = 65,\
                     temperature = 0.5,\
                     sparkWhenWithoutEmbedding = False
                     ):
        '''
        参数解释：
            - wikiPromptTpl: wiki 大模型问答模板，在某些场景服务默认的 prompt 回答效果不好时，业务可以考虑通过自定义 prompt 来改善。<wikiquestion>替换的问题标识，<wikicontent>替换的文本内容标识
            - wikiFilterScore: wiki 结果分数阈值，低于这个阈值的结果丢弃。取值范围为(0,1] 参考值为：0.80非常宽松 0.82宽松 0.83标准0.84严格 0.86非常严格。
            - temperature: 大模型问答时的温度，取值 0-1，temperature 越大，大模型回答随机度越高
            - sparkWhenWithoutEmbedding: 用户问题未匹配到文档内容时，是否使用大模型兜底回答问题
        '''
        
        self.appId = APPId
        self.apiSecret = APISecret
        #self.timeStamp = TimeStamp
        self.originUrl  = "wss://chatdoc.xfyun.cn/openapi/chat"
        
        self.chatExtends =  {
                            "wikiPromptTpl": wikiPromptTpl,
                            "wikiFilterScore": wikiFilterScore,
                            "temperature": temperature,
                            'sparkWhenWithoutEmbedding':sparkWhenWithoutEmbedding
                            }

    def get_origin_signature(self):
        self.timeStamp = str(int(time.time()))
        m2 = hashlib.md5()
        data = bytes(self.appId + self.timeStamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum

    def get_signature(self):
        # 获取原始签名
        signature_origin = self.get_origin_signature()
        # print(signature_origin)
        # 使用加密键加密文本
        signature = hmac.new(self.apiSecret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        # base64密文编码
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        # print(signature)
        return signature

    def get_header(self):
        signature = self.get_signature()
        header = {
            "Content-Type": "application/json",
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return header

    def get_url(self):
        signature = self.get_signature()
        header = {
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return self.originUrl + "?" + f'appId={self.appId}&timestamp={self.timeStamp}&signature={signature}'
        # 使用urlencode会导致签名乱码
        # return self.originUrl + "?" + urlencode(header)


    def chat(self,body):
        if 'chatExtends' not in body.keys():
            body['chatExtends'] = self.chatExtends
        global recep_mesg # 2
        # print('#3',recep_mesg) # 3
        recep_mesg = []
        # print('#4',recep_mesg) # 4
        wsUrl = self.get_url()
        #print(wsUrl)
        #recep_mesg = []
        
        # 禁用WebSocket库的跟踪功能，使其不再输出详细的调试信息。
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(wsUrl,\
                                    on_message=on_message,\
                                    on_error=on_error,\
                                    on_close=on_close,\
                                    on_open=on_open)
        ws.appid = self.appId
        ws.question = body
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        print('#6',recep_mesg)
        return recep_mesg
    
    def embellish_message_func(self,recep_mesg):
        '''
        

        Parameters
        ----------
        recep_mesg : TYPE
            websocket输出的内容列表.

        Returns
        -------
        TYPE
            完整输出一句话.
        fileRefer : TYPE
            status==99,是援引的目录.

        '''
        output = []
        fileRefer = {}
        for mes in recep_mesg:
            if (mes['code'] == 0)&(mes['status'] in [1,2] ):
                if 'content' in mes.keys():
                    output.append(mes['content'])
            elif mes['status'] == 99:
                fileRefer = eval(mes['fileRefer'])
            elif (mes['code'] in [10013,62001])&(mes['status'] in [1,2] ):
                output.append(mes['content'])
                fileRefer = {}
        return ''.join(output),fileRefer
    
    

if __name__ == '__main__':
    APPId = "xxxx"
    APISecret = "xxxxxx"
    doc_qa = Document_Q_And_A(APPId, APISecret)

    # 单轮对话
    body = {
        
        'chatExtends' :  {
                            "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                            "wikiFilterScore": 65,
                            "temperature": 0.5,
                            'sparkWhenWithoutEmbedding':False
                            },
        
        
        "fileIds": [
            "xxxxx"
        ],
        "messages": [
            {
                "role": "user",
                "content": "父亲要走的时候，去买了什么东西？"
            }
        ]
    }
    recep_mesg = doc_qa.chat(body)
    doc_qa.embellish_message_func(recep_mesg)
    
    
    # 多轮对话
    body = {
        "fileIds": [
            "xxxxxx"
        ],
        "messages": [
            {
                "role": "user",
                "content": "父亲要走的时候，去买了什么东西？"
            },
            {
                "role": "user",
                "content": "如何理赔"
            },
            {
                "role": "assistant",
                "content": "您好，根据您提供的信息，理赔操作指引如下：\n\n1. 登录小程序，点击“理赔申请”。\n2. 选择对应保单。\n3. 上传理赔相关资料。\n4. 填写发票总金额。\n5. 填写银行账户，需精确到支行。\n6. 点击“提交”成功后，返回“理赔服务”界面，点选“理赔查询”，查看理赔进度和申请记录。\n7. 如有需要，点击“查看详情”，查看理赔详情和金额。\n\n请注意，如有严重既往症员工还请和HR部门及时报备沟通，如未及时报备，保险公司不承担相关责任。同时，索赔资料不齐全导致延迟赔付等问题也需要注意。"
            },
            {
              "role": "user",
              "content": "家属有什么福利"
            }
        ]
    }
    doc_qa.chat(body)
    recep_mesg