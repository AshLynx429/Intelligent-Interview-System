import sys
import os

# 把 src 目录加到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from model_service import ModelService

print("正在加载模型，请稍候...")
service = ModelService()
print("模型加载成功！")

response = service.model.chat(service.tokenizer, "你好，请介绍一下你自己", history=[])
print("模型回答：", response)