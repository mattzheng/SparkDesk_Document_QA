import math
import gradio as gr
import plotly.express as px
import numpy as np

small_and_beautiful_theme = gr.themes.Soft(
        primary_hue=gr.themes.Color(
            c50="#EBFAF2",
            c100="#CFF3E1",
            c200="#A8EAC8",
            c300="#77DEA9",
            c400="#3FD086",
            c500="#02C160",
            c600="#06AE56",
            c700="#05974E",
            c800="#057F45",
            c900="#04673D",
            c950="#2E5541",
            name="small_and_beautiful",
        ),
        secondary_hue=gr.themes.Color(
            c50="#576b95",
            c100="#576b95",
            c200="#576b95",
            c300="#576b95",
            c400="#576b95",
            c500="#576b95",
            c600="#576b95",
            c700="#576b95",
            c800="#576b95",
            c900="#576b95",
            c950="#576b95",
        ),
        neutral_hue=gr.themes.Color(
            name="gray",
            c50="#f6f7f8",
            # c100="#f3f4f6",
            c100="#F2F2F2",
            c200="#e5e7eb",
            c300="#d1d5db",
            c400="#B2B2B2",
            c500="#808080",
            c600="#636363",
            c700="#515151",
            c800="#393939",
            # c900="#272727",
            c900="#2B2B2B",
            c950="#171717",
        ),
        radius_size=gr.themes.sizes.radius_sm,
    ).set(
        # button_primary_background_fill="*primary_500",
        button_primary_background_fill_dark="*primary_600",
        # button_primary_background_fill_hover="*primary_400",
        # button_primary_border_color="*primary_500",
        button_primary_border_color_dark="*primary_600",
        button_primary_text_color="white",
        button_primary_text_color_dark="white",
        button_secondary_background_fill="*neutral_100",
        button_secondary_background_fill_hover="*neutral_50",
        button_secondary_background_fill_dark="*neutral_900",
        button_secondary_text_color="*neutral_800",
        button_secondary_text_color_dark="white",
        # background_fill_primary="#F7F7F7",
        # background_fill_primary_dark="#1F1F1F",
        # block_title_text_color="*primary_500",
        block_title_background_fill_dark="*primary_900",
        block_label_background_fill_dark="*primary_900",
        input_background_fill="#F6F6F6",
        # chatbot_code_background_color="*neutral_950",
        # gradio 会把这个几个chatbot打头的变量应用到其他md渲染的地方，鬼晓得怎么想的。。。
        chatbot_code_background_color_dark="*neutral_950",
    )


# spark 总结
from Document_upload_summary import Document_Upload_Summary
# spark 问答
from Document_Q_And_A import Document_Q_And_A,on_error,on_close,on_open,run,on_message
# 在Document_Q_And_A.py中的全局变量不会生效，所以不能通过直接print(recep_mesg)拿到答案


APPId = "xxx"
APISecret = "xxxxxxxx"

dus = Document_Upload_Summary(APPId, APISecret)
doc_qa = Document_Q_And_A(APPId, APISecret)


# 文件
valid_files_group = {'背影.txt':'27c64900ad6643c1a958af920942e461',                     
                    '人工智能生成内容白皮书 2022.pdf':'b4649d36cb0c477e911bb5fb5ef9736e',
                    '2023AIGC市场研究报告及ChatGPT推动的变革趋势与投资机会-甲子光年.pdf':'66393ee0bf5441e5bb606673f414b353',
                    'AIGC+AI生成内容产业展望报告-量子位-34页.pdf':'1e7a466009a645c6a4ff7e46784e4598'
                     }


with gr.Blocks(theme=small_and_beautiful_theme) as demo: # small_and_beautiful_theme 让页面边框变得简介
    with gr.Tab(label="知识库"):
        # 1 模块1
        with gr.Accordion(label="上传模块", open=True): # open可以选择下面整个模块是否显示
            use_websearch_checkbox = gr.Checkbox(label="使用在线搜索", 
                                                 value=False, 
                                                 elem_classes="switch-checkbox", 
                                                 elem_id="gr-websearch-cb", visible=False)
            index_files = gr.Files(label="上传", type="file", elem_id="upload-index-file")
            # two_column = gr.Checkbox(label="双栏pdf", value=False)
            upload_button = gr.Button("上传星火")
        
        gr.Markdown("---", elem_classes="hr-line")
        # 2 模块2
        with gr.Accordion(label="文档总结模块", open=True): # open可以选择下面整个模块是否显示
        
            FileSelectDropdown_first = gr.Dropdown( # 一级下拉菜单
                label="选择文档,一次只能选一份文档",
                choices= list(valid_files_group.keys()),
                multiselect=False,
                value=list(valid_files_group.keys())[0],
                container=False,
                # scale = 5,
                interactive = True
            )
        
            with gr.Row():  # 模块按列排布
            
                doc_summary_btn = gr.Button("文档总结",size = 'sm',scale = 1,variant = 'primary')
                
                SparkInputText_first = gr.Textbox( 
                    show_label=True,
                    placeholder="在这输入内容",
                    label="文档概要",
                    value='文档摘要',
                    lines=8,
                    scale = 5,
                    interactive = False
                )

        gr.Markdown("---", elem_classes="hr-line")
        # 3 模块3
        with gr.Accordion(label="问答模块", open=True): # open可以选择下面整个模块是否显示
            with gr.Row():  # 模块按列排布
                # with gr.Column(scale=5):
                FileSelectDropdown = gr.Dropdown( # 一级下拉菜单
                    label="选择模板集合文件",
                    choices= list(valid_files_group.keys()),
                    multiselect=True,
                    value=list(valid_files_group.keys())[0],
                    container=False,
                    # scale = 5,
                    interactive = True
                )
                # templateRefreshBtn = gr.Button("🔄 刷新",size = 'sm',scale = 1) # 刷新按钮
        
            with gr.Row():  # 模块按列排布        
                #with gr.Accordion(label="问答模块", open=True): # open可以选择下面整个模块是否显示
                SparkInputText = gr.Textbox( 
                    show_label=True,
                    placeholder="在这输入内容",
                    label="输入框",
                    value='输入相关内容',
                    lines=8,
                    scale = 5,
                    interactive = True
                )
                # with gr.Column(): 
                doc_answer_btn = gr.Button("文档问答",size = 'sm',scale = 1,variant = 'primary')
                    
            
            SparkOutputText = gr.Textbox( 
                show_label=True,
                placeholder="在这显示内容",
                label="内容显示",
                value='显示问答内容',
                lines=8
            )
    
    # 上传星火
    def upload_button_func(index_files):
        # 输入：无输入项
        # 输出：更新【一级下拉】选项，【二级下拉】置空
        # 触发方式: click点击行为
        global valid_files_group

        for file in index_files:
            # file_path = 'aigc相关报告/AIGC+AI生成内容产业展望报告-量子位-34页.pdf'
            print(file.name)
            files = {'file': open(file.name, 'rb')}
            body = {
                        "url": "",
                        "fileName": file.name.split('/')[-1],
                        "fileType": "wiki",     # 固定值
                        "needSummary": False,
                        "stepByStep": False,
                        "callbackUrl": "your_callbackUrl",
                    }
            
            response = dus.upload_files(files,body)
            
            # 赋值
            valid_files_group[file.name.replace('\\','/').split('/')[-1]] = response.json()["data"]["fileId"]

        # for file in index_files:
        #     valid_files_group[file.name.replace('\\','/').split('/')[-1]] = 'fileid'
        return gr.Dropdown.update(choices=list(valid_files_group.keys()),value = list(valid_files_group.keys())[0]  ),\
            gr.Dropdown.update(choices=list(valid_files_group.keys()),value = list(valid_files_group.keys())[0]  )

    
    upload_button.click(upload_button_func, [index_files], 
                             [FileSelectDropdown_first,FileSelectDropdown])
    
    # 文档总结
    def doc_summary_button_func(FileSelectDropdown_first):
        # 输入：无输入项
        # 输出：更新【一级下拉】选项，【二级下拉】置空
        # 触发方式: click点击行为
        
        fileid = valid_files_group[FileSelectDropdown_first]
        # print('fileid',fileid)
        response = dus.file_summary(fileid)
        summary = response.json()
        # spark_output_text = f"文件名是：{'++'.join(FileSelectDropdown)}，输入是：{SparkInputText}"
        print('summary',summary)
        if (summary['code'] == 0)&(summary['data']==summary['data']):      
            return summary['data']['summary']
        else:
            return f'未调用成功,报错输出为:{str(summary)}'
        
        
    doc_summary_btn.click(doc_summary_button_func, [FileSelectDropdown_first], 
                             [SparkInputText_first])
    
    
    # 文档问答
    def doc_answer_button_func(FileSelectDropdown,SparkInputText):
        # 输入：无输入项
        # 输出：更新【一级下拉】选项，【二级下拉】置空
        # 触发方式: click点击行为
        global valid_files_group
        valid_files_group_reversal = {v:k for k,v in valid_files_group.items()}
        # 单轮对话
        body = {
            "fileIds": [valid_files_group[file] for file in FileSelectDropdown],
            "messages": [
                {
                    "role": "user",
                    "content": SparkInputText
                }
            ]
        }
        recep_mesg = doc_qa.chat(body)
        message,fileRefer = doc_qa.embellish_message_func(recep_mesg)
        
        fileRefer_cont = {valid_files_group_reversal[k]:v  for k,v in fileRefer.items()}
        
        final_mesg = message + f'\n\n文献参考:\n{str(fileRefer_cont)}'
        return final_mesg

    doc_answer_btn.click(doc_answer_button_func, [FileSelectDropdown,SparkInputText], 
                             [SparkOutputText])
    
    
if __name__ == "__main__":
    demo.queue().launch()
