# SparkDesk_Document_QA

博客地址：[讯飞星火知识库文档问答Web API的使用（二）](https://blog.csdn.net/sinat_26917383/article/details/134599259)

![在这里插入图片描述](https://github.com/mattzheng/SparkDesk_Document_QA/blob/main/sparkdesk.png)

# 1 SparkDesk的文档问答
SparkDesk的文档问答模块相关文档与地址：
- 官方演示地址: https://chatdoc.xfyun.cn/chat
- [星火知识库 API 文档](https://www.xfyun.cn/doc/spark/ChatDoc-API.html#%E4%B8%80%E3%80%81%E6%9C%8D%E5%8A%A1%E4%BB%8B%E7%BB%8D)
- [embedding API 文档](https://www.xfyun.cn/doc/spark/Embedding_new_api.html#_1-%E6%9C%8D%E5%8A%A1%E6%8F%8F%E8%BF%B0)

本篇记录的是通过星火知识库Web API +ChuanhuGPT 的一个实验项目

> 吐槽一下：
星火文档问答官方开放的代码不咋地，可能没啥人用，拿个半成品就挂官方了？？ 讯飞的AI社区官方感觉也不咋运营...

知识库web api整体结构还是简单的，不过跟在线的版本，有一些功能上的阉割：
- 文档上传
- 文档总结/摘要
- 文档问答



知识库API 第一次申请会给1000次额度：
![在这里插入图片描述](https://img-blog.csdnimg.cn/fbf1b051b1c94f7ab205e9da1989c280.png)
# 2 代码示例



笔者稍微打包了一下，具体代码放到了我的github：[SparkDesk_Document_QA](https://github.com/mattzheng/SparkDesk_Document_QA)：
- `Document_upload_summary.py`：文档上传 + 文档总结
- `Document_Q_And_A.py`：文档问答

使用前需申请一下api key + 安装依赖：
```
pip install websocket -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install websocket-client -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install requests_toolbelt -i https://pypi.tuna.tsinghua.edu.cn/simple

```


## 2.1 文档上传+文档总结

官方关于文档总结有两个接口，我就没看懂这俩啥区别。。所以只封装一个进来，与文档上传放在一个类中。
官方文档：[ChatDoc](https://www.xfyun.cn/doc/spark/ChatDoc-API.html#%E4%B8%89%E3%80%81%E6%8E%A5%E5%8F%A3%E5%88%97%E8%A1%A8) 

文档上传规范：
上传知识库文档数据，目前支持 doc/docx、pdf、md、txt 格式，单文件大小不超过 20MB，不超过 100W 字符。

文档上传参数含义：
![在这里插入图片描述](https://img-blog.csdnimg.cn/0d39c6bc36e14c8eabb13ad99f45d491.png)
文档上传返回参数详情：
![在这里插入图片描述](https://img-blog.csdnimg.cn/26d4b17fff284faba2140428de3d299a.png)
文档总结参数请求：
![在这里插入图片描述](https://img-blog.csdnimg.cn/8417791fa08c4089acd89f5385f96b49.png)
文档总结输出内容：
![在这里插入图片描述](https://img-blog.csdnimg.cn/ba096948dfb64e9cac64044cf2002c44.png)



本地文档上传示例：

```
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
```
其中，注意，
- 文档上传还是一个个上传比较好，需要记录下fileid，之后对话就是根据这个进行问答；
- 文档上传可以用URL



## 2.2 文档对话
这里本来是支持流式输出的，笔者改成了一次性全部输出，是通过global的方式
此时额外学了一下websocket：[python中使用websocket调用、获取、保存大模型API](https://blog.csdn.net/sinat_26917383/article/details/134124585)

官方文档：[ChatDoc](https://www.xfyun.cn/doc/spark/ChatDoc-API.html#%E4%B8%89%E3%80%81%E6%8E%A5%E5%8F%A3%E5%88%97%E8%A1%A8) 

文档对话的参数：
![在这里插入图片描述](https://img-blog.csdnimg.cn/89f72c4f3a3c46788dc8f6ab5b54d0b1.png)
输出参数详情：
![在这里插入图片描述](https://img-blog.csdnimg.cn/834a0c54ffcf43adafb315a44f1662d6.png)

若返回 fileRefer 为空，提示 "抱款，在文档中没有找到与提问相关的内容，请尝试换个问题问问吧。"表示提问未匹配到文档内容，可以降低chatExtends.wikiFilterScore以降低匹配阈值，也可以开启chatExtends.sparkWhenWithoutEmbedding用大模型兜底



单轮对话：
```
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
```
其中，
websocket是把一句话流式，一个片段一个片段的输出，`embellish_message_func`就是把这些拼装起来；
body中`chatExtends` 可以不设置，也有默认；`fileIds` 是之前上传的field，可以支持多个field




多轮对话：
```
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
```
如上进行多轮对话输出



## 2.3 其他知识库高级功能
> 星火知识库服务还提供 自定义切分、OCR 识别、文档内容查询、内容相似度检索等功能，如有需要请联系cbg_open_ml@iflytek.com
貌似没理我，暂时没申请到...
